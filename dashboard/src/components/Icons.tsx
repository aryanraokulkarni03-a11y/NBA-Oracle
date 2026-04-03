import type { SVGProps } from "react";

type IconName =
  | "overview"
  | "today"
  | "performance"
  | "stability"
  | "learning"
  | "providers"
  | "operations"
  | "guide"
  | "refresh"
  | "warning"
  | "spark"
  | "activity"
  | "shield"
  | "mail"
  | "send";

const ICON_PATHS: Record<IconName, string[]> = {
  overview: ["M3.5 4.5h7v7h-7z", "M13.5 4.5h7v4h-7z", "M13.5 11.5h7v10h-7z", "M3.5 14.5h7v7h-7z"],
  today: ["M6 3.5v3", "M18 3.5v3", "M4 8.5h16", "M5.5 5.5h13a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1h-13a1 1 0 0 1-1-1v-12a1 1 0 0 1 1-1z"],
  performance: ["M5 18.5h14", "M7.5 16v-5.5", "M12 16V7.5", "M16.5 16V11"],
  stability: ["M12 3.5l7 2.8v5.4c0 4.4-2.7 8.2-7 9.8-4.3-1.6-7-5.4-7-9.8V6.3z", "M9.5 12l1.7 1.7 3.8-3.8"],
  learning: ["M8 6.5a4 4 0 1 1 0 8", "M16 6.5a4 4 0 1 0 0 8", "M10.5 8.5h3", "M10.5 15.5h3"],
  providers: ["M4 6.5h16", "M4 12h16", "M4 17.5h16", "M6.5 5a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3z", "M17.5 10.5a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3z", "M10.5 16a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3z"],
  operations: ["M12 4.5v15", "M4.5 12h15", "M7.5 7.5l9 9", "M16.5 7.5l-9 9"],
  guide: ["M6 4.5h9", "M6 9h12", "M6 13.5h10", "M6 18h12", "M18.5 4.5v6l-2-1-2 1v-6"],
  refresh: ["M20 6v5h-5", "M4 18v-5h5", "M6.5 9a6.5 6.5 0 0 1 11-2", "M17.5 15a6.5 6.5 0 0 1-11 2"],
  warning: ["M12 4.5 20 19.5H4z", "M12 9v4.5", "M12 16.5h.01"],
  spark: ["M12 4.5l1.6 4.4 4.4 1.6-4.4 1.6-1.6 4.4-1.6-4.4-4.4-1.6 4.4-1.6z"],
  activity: ["M4 12h3l2-4 3 9 3-6 2 1h3"],
  shield: ["M12 3.5l7 2.8v5.4c0 4.4-2.7 8.2-7 9.8-4.3-1.6-7-5.4-7-9.8V6.3z"],
  mail: ["M4.5 6.5h15a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1h-15a1 1 0 0 1-1-1v-9a1 1 0 0 1 1-1z", "M4.5 8l7.5 5 7.5-5"],
  send: ["M20 4 10 14", "M20 4l-6 16-4-6-6-4z"],
};

export function Icon({ name, className, ...props }: SVGProps<SVGSVGElement> & { name: IconName }) {
  const paths = ICON_PATHS[name];
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      className={className}
      {...props}
    >
      {paths.map((path, index) => (
        <path key={`${name}-${index}`} d={path} />
      ))}
    </svg>
  );
}
