import DOMPurify from "dompurify";

export function sanitizeText(
  rawText,
  allowedTags = ["p", "br", "a", "strong", "b", "em", "i", "ul", "ol", "li"],
  allowedAttr = ["href", "target"],
) {
  if (!rawText) return null;
  if (typeof rawText != string) return null;

  return DOMPurify.sanitize(rawText, {
    ALLOWED_TAGS: allowedTags,
    ALLOWED_ATTR: allowedAttr,
  });
}
