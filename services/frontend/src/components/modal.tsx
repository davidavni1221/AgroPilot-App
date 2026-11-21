"use client";

import { X } from "lucide-react";
import { useEffect, useId, useRef } from "react";

/**
 * A window in the middle of the screen, with an X. It is the browser's own <dialog>, so Esc closes it, focus stays inside it,
 * and the page behind cannot be tapped. Mount it only while it is open: each opening then starts with an empty form.
 * Clicking the dark area outside also closes it.
 */
export function Modal({ title, onClose, children }: { title: string; onClose: () => void; children: React.ReactNode }) {
  const dialog = useRef<HTMLDialogElement>(null);
  const titleId = useId();

  useEffect(() => {
    dialog.current?.showModal();
    const before = document.body.style.overflow;
    document.body.style.overflow = "hidden"; // the page does not scroll behind the window
    return () => {
      document.body.style.overflow = before;
    };
  }, []);

  return (
    <dialog
      ref={dialog}
      aria-labelledby={titleId}
      onClose={onClose}
      onClick={(event) => {
        if (event.target === dialog.current) onClose();
      }}
      className="m-auto max-h-[90dvh] w-[calc(100%-1.5rem)] max-w-lg overflow-y-auto rounded-2xl bg-background p-0 text-foreground shadow-xl ring-1 ring-foreground/10 backdrop:bg-black/50"
    >
      <div className="sticky top-0 z-10 flex items-center justify-between gap-3 bg-background px-5 py-4">
        <h2 id={titleId} className="text-2xl font-bold">
          {title}
        </h2>
        <button
          type="button"
          onClick={onClose}
          aria-label="Close"
          className="flex size-11 shrink-0 items-center justify-center rounded-full ring-1 ring-foreground/15 transition-colors hover:bg-secondary focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
        >
          <X aria-hidden className="size-5" />
        </button>
      </div>
      <div className="px-5 pb-5">{children}</div>
    </dialog>
  );
}
