import type { AnchorHTMLAttributes, ButtonHTMLAttributes, ReactNode } from "react";

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

type AnchorButtonProps = SharedButtonProps &
  AnchorHTMLAttributes<HTMLAnchorElement> & {
    href: string;
  };

type NativeButtonProps = SharedButtonProps &
  ButtonHTMLAttributes<HTMLButtonElement> & {
    href?: never;
  };

export function Button(props: AnchorButtonProps | NativeButtonProps) {
  const { children, variant = "primary", className = "", ...rest } = props;
  const classes = [
    "inline-flex h-11 items-center justify-center rounded-full border px-5 text-sm font-semibold transition focus:outline-none focus-visible:ring-4 focus-visible:ring-red/15 active:translate-y-px",
    variantClasses[variant],
    className,
  ].join(" ");

  if ("href" in props) {
    return (
      <a className={classes} {...(rest as AnchorHTMLAttributes<HTMLAnchorElement>)} href={props.href}>
        {children}
      </a>
    );
  }

  return (
    <button className={classes} {...(rest as ButtonHTMLAttributes<HTMLButtonElement>)}>
      {children}
    </button>
  );
}
