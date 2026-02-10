import DOMPurify from "dompurify";

export function sanitizeRawHTML(
    rawHTML,
    allowedTags = ["p", "br", "a", "strong", "b", "em", "i", "ul", "ol", "li"],
    allowedAttr = ["href", "target"],
) {
    if (!rawHTML) return null;

    return DOMPurify.sanitize(rawHTML, {
        ALLOWED_TAGS: allowedTags,
        ALLOWED_ATTR: allowedAttr,
    });
}
