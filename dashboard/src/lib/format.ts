export function formatDateTime(value?: string | null) {
  if (!value) {
    return "n/a";
  }
  try {
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date(value));
  } catch {
    return value;
  }
}

export function formatPercent(value?: number | null, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "n/a";
  }
  return `${(value * 100).toFixed(digits)}%`;
}

export function formatAmericanOdds(value?: number | null) {
  if (value === null || value === undefined) {
    return "n/a";
  }
  return value > 0 ? `+${value}` : `${value}`;
}

export function formatCount(value?: number | null) {
  if (value === null || value === undefined) {
    return "0";
  }
  return String(value);
}

export function formatRecord(correct?: number | null, total?: number | null) {
  return `${formatCount(correct)}/${formatCount(total)}`;
}

export function toHeadline(value?: string | null) {
  if (!value) {
    return "Unknown";
  }
  return value
    .replace(/[_-]+/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

export function formatRelativeStatus(value?: string | null) {
  if (!value) {
    return "Unknown";
  }
  return value.replace(/_/g, " ");
}

export function formatReadableText(value?: string | null) {
  if (!value) {
    return "Unknown";
  }
  if (/[A-Z]/.test(value) || value.includes(" ")) {
    return value;
  }
  return toHeadline(formatRelativeStatus(value));
}

export function formatCompactId(value?: string | null, head = 12, tail = 6) {
  if (!value) {
    return "n/a";
  }
  if (value.length <= head + tail + 1) {
    return value;
  }
  return `${value.slice(0, head)}...${value.slice(-tail)}`;
}
