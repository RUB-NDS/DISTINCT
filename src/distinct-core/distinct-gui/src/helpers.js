import { FQP } from "filter-query-parser"

const timestampToDate = (timestamp) => {
  const date = new Date(timestamp * 1000)
  return date.toLocaleString()
}

const filterReports = (reports, sq) => {
  if (sq == '') return reports
  const filter = FQP.parser(sq)
  return reports.filter((report) => {
    return checkCondition(report, filter)
  })
}

/**
 Bug: (type = "documentinteractive" and content.html contains "POCs") or type = "documentinit"
 Works: type = "documentinit" or (type = "documentinteractive" and content.html contains "POCs")
 */

const checkCondition = (report, condition) => {
  window.evalStr = ''
  if (condition.condition == 'AND') {
    window.evalStr += '('
    andCondition(report, condition.rules)
  } else if (condition.condition == 'OR') {
    window.evalStr += '('
    orCondition(report, condition.rules)
  }
  // console.log(window.evalStr)
  return eval(window.evalStr) ? true : false
}

const andCondition = (report, rules) => {
  // console.log(`and: ${JSON.stringify(rules)}`)
  for (const [i, rule] of rules.entries()) {
    if (rule.field) {
      window.evalStr += checkRule(report, rule)
      if (i != rules.length - 1) window.evalStr += ' && '
    } else if (rule.condition == 'AND') {
      window.evalStr += '('
      andCondition(report, rule.rules)
    } else if (rule.condition == 'OR') {
      window.evalStr += '('
      orCondition(report, rule.rules)
    }
  }
  window.evalStr += ')'
}

const orCondition = (report, rules) => {
  // console.log(`or: ${JSON.stringify(rules)}`)
  for (const [i, rule] of rules.entries()) {
    if (rule.field) {
      window.evalStr += checkRule(report, rule)
      if (i != rules.length - 1) window.evalStr += ' || '
    } else if (rule.condition == 'AND') {
      window.evalStr += '('
      andCondition(report, rule.rules)
    } else if (rule.condition == 'OR') {
      window.evalStr += '('
      orCondition(report, rule.rules)
    }
  }
  window.evalStr += ')'
}

const checkRule = (report, rule) => {
  // console.log(`checkrule: ${JSON.stringify(rule)}`)
  const { field, operator, value } = rule

  if (field == 'id') {
    return compare(operator, report.id, value) // int
  } else if (field == 'timestamp') {
    return compare(operator, report.val.timestamp, value) // int
  } else if (field == 'type') {
    return compare(operator, report.key, value) // str
  } else if (field == 'hierarchy') {
    return compare(operator, report.val.hierarchy, value) // str
  } else if (field == 'url') {
    return compare(operator, report.val.href, value) // str
  } else if (field.startsWith('content.') && field.split('.')[1] in report.val) {
    return compare(operator, report.val[field.split('.')[1]], value)
  } else if (field.startsWith('content.') && !(field.split('.')[1] in report.val)) {
    return 0
  } else {
    throw new Error(`Unknown field: ${field}`)
  }
}

const compare = (op, a, b) => {
  switch (op) {
    case '=':
      return a == b ? 1 : 0
    case '!=':
      return a != b ? 1 : 0
    case '>=':
      return a >= b ? 1 : 0
    case '<=':
      return a <= b ? 1 : 0
    case '>':
      return a > b ? 1 : 0
    case '<':
      return a < b ? 1 : 0
    case 'CONTAINS':
      return a.includes(b) ? 1 : 0
    case 'STARTS WITH':
      return a.startsWith(b) ? 1 : 0
    case 'ENDS WITH':
      return a.endsWith(b) ? 1 : 0
    case 'DOES NOT CONTAIN':
      return !a.includes(b) ? 1 : 0
    default:
      throw new Error(`Unknown operator: ${op}`)
  }
}

export {
  timestampToDate,
  filterReports,
  compare
}
