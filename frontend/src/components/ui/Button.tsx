"use client";

import Link from "next/link";
import type { ButtonHTMLAttributes, ReactNode } from "react";

type ButtonVariant = "primary" | "pink" | "outline" | "ghost";

const variantClasses: Record<ButtonVariant, string> = {
  primary: "border-transparent bg-red text-paper shadow-red-soft hover:bg-red-dark",
  pink: "border-transparent bg-pink-deep text-ink shadow-pink-soft hover:bg-pink-deep-dark",
  outline: "border-border bg-transparent text-ink hover:border-red hover:text-red",
  ghost: "border-transparent bg-transparent text-muted hover:text-red",
};

type SharedButtonProps = {
  children: ReactNode;
  variant?: ButtonVariant;
  className?: string;
};

type LinkButtonProps = SharedButtonProps & {
  href: string;
};

type NativeButtonProps = SharedButtonProps &
  ButtonHTMLAttributes<HTMLButtonElement> & {
    href?: never;
  };

export function Button(props: LinkButtonProps | NativeButtonProps) {
  const { children, variant = "primary", className = "", ...rest } = props;
  const classes = [
    "pressable inline-flex h-11 items-center justify-center rounded-full border px-5 text-sm font-semibold whitespace-nowrap focus:outline-none focus-visible:ring-4 focus-visible:ring-red/15 disabled:pointer-events-none",
    variantClasses[variant],
    className,
  ].join(" ");

  if ("href" in props && props.href) {
    const { href, ...linkRest } = props as LinkButtonProps;
    return (
      <Link
        href={href}
        className={classes}
        {...(linkRest as Omit<LinkButtonProps, "href" | "variant" | "className">)}
      >
        {children}
      </Link>
    );
  }

  return (
    <button className={classes} {...(rest as ButtonHTMLAttributes<HTMLButtonElement>)}>
      {children}
    </button>
  );
}
