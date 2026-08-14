export type FloatingChatKind = "tutor" | "classroom";

const FLOATING_CHAT_OPEN_EVENT = "edumind:floating-chat-open";

export function announceFloatingChatOpen(kind: FloatingChatKind) {
  window.dispatchEvent(new CustomEvent<FloatingChatKind>(FLOATING_CHAT_OPEN_EVENT, { detail: kind }));
}

export function subscribeToFloatingChatOpen(listener: (kind: FloatingChatKind) => void) {
  const handler = (event: Event) => listener((event as CustomEvent<FloatingChatKind>).detail);
  window.addEventListener(FLOATING_CHAT_OPEN_EVENT, handler);
  return () => window.removeEventListener(FLOATING_CHAT_OPEN_EVENT, handler);
}
