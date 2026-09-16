const methods = ['get', 'post', 'put', 'patch', 'delete'];

const resolveSchema = (document, schema, seen = new Set()) => {
  if (!schema?.$ref) return schema;
  if (seen.has(schema.$ref)) return schema;
  seen.add(schema.$ref);
  const resolved = schema.$ref.slice(2).split('/').reduce((value, key) => value?.[key], document);
  return resolveSchema(document, resolved, seen);
};

const values = (value) => new Set(value ?? []);
const isSubset = (subset, superset) => [...subset].every((item) => superset.has(item));
const normalizedType = (schema) => JSON.stringify(Array.isArray(schema?.type) ? [...schema.type].sort() : schema?.type ?? null);
const hasKeyword = (schema, keyword) => schema && Object.hasOwn(schema, keyword);

function compareSchema(beforeDocument, afterDocument, beforeInput, afterInput, mode, location, differences, seenPairs = new Set()) {
  const before = resolveSchema(beforeDocument, beforeInput);
  const after = resolveSchema(afterDocument, afterInput);
  if (!before || !after) {
    if (mode === 'request' && !before && after) differences.push(`${location}: request schema was added`);
    if (mode === 'response' && before && !after) differences.push(`${location}: response schema was removed`);
    return;
  }
  const pairKey = `${beforeInput?.$ref ?? location}|${afterInput?.$ref ?? location}|${mode}`;
  if (seenPairs.has(pairKey)) return;
  seenPairs.add(pairKey);

  if (normalizedType(before) !== normalizedType(after)) differences.push(`${location}: type changed from ${normalizedType(before)} to ${normalizedType(after)}`);
  if (before.format !== after.format) {
    if ((mode === 'request' && after.format !== undefined) || (mode === 'response' && before.format !== undefined)) {
      differences.push(`${location}: format became incompatible for ${mode}`);
    }
  }
  if (before.pattern !== after.pattern) {
    if ((mode === 'request' && after.pattern !== undefined) || (mode === 'response' && before.pattern !== undefined)) {
      differences.push(`${location}: pattern became incompatible for ${mode}`);
    }
  }
  const beforeAdditional = hasKeyword(before, 'additionalProperties') ? before.additionalProperties : true;
  const afterAdditional = hasKeyword(after, 'additionalProperties') ? after.additionalProperties : true;
  if (mode === 'request') {
    if (
      (beforeAdditional === true && afterAdditional !== true) ||
      (beforeAdditional !== false && afterAdditional === false)
    ) differences.push(`${location}: additionalProperties narrowed for request`);
  } else if (
    (beforeAdditional === false && afterAdditional !== false) ||
    (beforeAdditional !== true && beforeAdditional !== false && afterAdditional === true)
  ) differences.push(`${location}: additionalProperties guarantee widened for response`);
  if (
    beforeAdditional && typeof beforeAdditional === 'object' &&
    afterAdditional && typeof afterAdditional === 'object'
  ) {
    compareSchema(
      beforeDocument,
      afterDocument,
      beforeAdditional,
      afterAdditional,
      mode,
      `${location}.*`,
      differences,
      new Set(seenPairs),
    );
  }

  const beforeHasEnum = hasKeyword(before, 'enum');
  const afterHasEnum = hasKeyword(after, 'enum');
  if (beforeHasEnum || afterHasEnum) {
    const compatible = mode === 'request'
      ? !afterHasEnum || (beforeHasEnum && isSubset(values(before.enum), values(after.enum)))
      : !beforeHasEnum || (afterHasEnum && isSubset(values(after.enum), values(before.enum)));
    if (!compatible) differences.push(`${location}: enum became incompatible for ${mode}`);
  }
  const beforeHasConst = hasKeyword(before, 'const');
  const afterHasConst = hasKeyword(after, 'const');
  if (before.const !== after.const && (beforeHasConst || afterHasConst)) {
    const compatible = mode === 'request' ? !afterHasConst : !beforeHasConst;
    if (!compatible) differences.push(`${location}: const became incompatible for ${mode}`);
  }
  if (JSON.stringify(before.not) !== JSON.stringify(after.not)) {
    if ((mode === 'request' && after.not !== undefined) || (mode === 'response' && before.not !== undefined)) {
      differences.push(`${location}: not constraint became incompatible for ${mode}`);
    }
  }

  for (const [minimumKey, maximumKey] of [
    ['minimum', 'maximum'],
    ['exclusiveMinimum', 'exclusiveMaximum'],
    ['minLength', 'maxLength'],
    ['minItems', 'maxItems'],
    ['minProperties', 'maxProperties'],
    ['minContains', 'maxContains'],
  ]) {
    const beforeMinimum = before[minimumKey];
    const afterMinimum = after[minimumKey];
    const beforeMaximum = before[maximumKey];
    const afterMaximum = after[maximumKey];
    if (mode === 'request') {
      if (afterMinimum !== undefined && (beforeMinimum === undefined || afterMinimum > beforeMinimum)) differences.push(`${location}: ${minimumKey} was narrowed`);
      if (afterMaximum !== undefined && (beforeMaximum === undefined || afterMaximum < beforeMaximum)) differences.push(`${location}: ${maximumKey} was narrowed`);
    } else {
      if (beforeMinimum !== undefined && (afterMinimum === undefined || afterMinimum < beforeMinimum)) differences.push(`${location}: ${minimumKey} response guarantee was widened`);
      if (beforeMaximum !== undefined && (afterMaximum === undefined || afterMaximum > beforeMaximum)) differences.push(`${location}: ${maximumKey} response guarantee was widened`);
    }
  }

  const beforeRequired = values(before.required);
  const afterRequired = values(after.required);
  if (mode === 'request') {
    for (const property of afterRequired) if (!beforeRequired.has(property)) differences.push(`${location}.${property}: became required in request`);
  } else {
    for (const property of beforeRequired) if (!afterRequired.has(property)) differences.push(`${location}.${property}: is no longer guaranteed in response`);
  }

  for (const [property, beforeProperty] of Object.entries(before.properties ?? {})) {
    const afterProperty = after.properties?.[property];
    if (!afterProperty) {
      differences.push(`${location}.${property}: property was removed`);
      continue;
    }
    compareSchema(beforeDocument, afterDocument, beforeProperty, afterProperty, mode, `${location}.${property}`, differences, new Set(seenPairs));
  }
  if (before.items || after.items) compareSchema(beforeDocument, afterDocument, before.items, after.items, mode, `${location}[]`, differences, new Set(seenPairs));
  for (const key of ['allOf', 'anyOf', 'oneOf']) {
    const beforeItems = before[key] ?? [];
    const afterItems = after[key] ?? [];
    if (key === 'allOf') {
      if (mode === 'request' && afterItems.length > beforeItems.length) differences.push(`${location}.${key}: request constraints were added`);
      if (mode === 'response' && afterItems.length < beforeItems.length) differences.push(`${location}.${key}: response guarantees were removed`);
    } else if (key === 'anyOf') {
      if (mode === 'request' && afterItems.length < beforeItems.length) differences.push(`${location}.${key}: request alternatives were removed`);
      if (mode === 'response' && afterItems.length > beforeItems.length) differences.push(`${location}.${key}: response alternatives were added`);
    } else if (beforeItems.length !== afterItems.length) {
      differences.push(`${location}.${key}: exclusive alternatives changed`);
    }
    for (let index = 0; index < Math.min(beforeItems.length, afterItems.length); index += 1) {
      compareSchema(beforeDocument, afterDocument, beforeItems[index], afterItems[index], mode, `${location}.${key}[${index}]`, differences, new Set(seenPairs));
    }
  }
}

const parameterKey = (parameter) => `${parameter.in}:${parameter.name}`;
const dereferenceParameter = (document, parameter) => resolveSchema(document, parameter);

export function findBreakingChanges(before, after) {
  const differences = [];
  for (const [path, beforePath] of Object.entries(before.paths ?? {})) {
    const afterPath = after.paths?.[path];
    if (!afterPath) {
      differences.push(`${path}: path was removed`);
      continue;
    }
    for (const method of methods) {
      const beforeOperation = beforePath[method];
      if (!beforeOperation) continue;
      const afterOperation = afterPath[method];
      const label = `${method.toUpperCase()} ${path}`;
      if (!afterOperation) {
        differences.push(`${label}: operation was removed`);
        continue;
      }
      if (beforeOperation.operationId !== afterOperation.operationId) differences.push(`${label}: operationId changed from ${beforeOperation.operationId} to ${afterOperation.operationId}`);

      const beforeParameters = new Map([...(beforePath.parameters ?? []), ...(beforeOperation.parameters ?? [])].map((parameter) => {
        const resolved = dereferenceParameter(before, parameter);
        return [parameterKey(resolved), resolved];
      }));
      const afterParameters = new Map([...(afterPath.parameters ?? []), ...(afterOperation.parameters ?? [])].map((parameter) => {
        const resolved = dereferenceParameter(after, parameter);
        return [parameterKey(resolved), resolved];
      }));
      for (const [key, beforeParameter] of beforeParameters) {
        const afterParameter = afterParameters.get(key);
        if (!afterParameter) {
          differences.push(`${label} parameter ${key}: was removed`);
          continue;
        }
        compareSchema(before, after, beforeParameter.schema, afterParameter.schema, 'request', `${label} parameter ${key}`, differences);
      }
      for (const [key, afterParameter] of afterParameters) {
        if (afterParameter.required && !beforeParameters.get(key)?.required) differences.push(`${label} parameter ${key}: became required`);
      }

      const beforeBody = beforeOperation.requestBody ? resolveSchema(before, beforeOperation.requestBody) : undefined;
      const afterBody = afterOperation.requestBody ? resolveSchema(after, afterOperation.requestBody) : undefined;
      if (afterBody?.required && !beforeBody?.required) differences.push(`${label}: request body became required`);
      for (const [mediaType, beforeMedia] of Object.entries(beforeBody?.content ?? {})) {
        const afterMedia = afterBody?.content?.[mediaType];
        if (!afterMedia) differences.push(`${label} request ${mediaType}: media type was removed`);
        else compareSchema(before, after, beforeMedia.schema, afterMedia.schema, 'request', `${label} request ${mediaType}`, differences);
      }

      for (const [status, beforeResponseInput] of Object.entries(beforeOperation.responses ?? {})) {
        const afterResponseInput = afterOperation.responses?.[status];
        if (!afterResponseInput) {
          differences.push(`${label} response ${status}: status was removed`);
          continue;
        }
        const beforeResponse = resolveSchema(before, beforeResponseInput);
        const afterResponse = resolveSchema(after, afterResponseInput);
        for (const [mediaType, beforeMedia] of Object.entries(beforeResponse.content ?? {})) {
          const afterMedia = afterResponse.content?.[mediaType];
          if (!afterMedia) differences.push(`${label} response ${status} ${mediaType}: media type was removed`);
          else compareSchema(before, after, beforeMedia.schema, afterMedia.schema, 'response', `${label} response ${status} ${mediaType}`, differences);
        }
      }
    }
  }
  return [...new Set(differences)];
}
