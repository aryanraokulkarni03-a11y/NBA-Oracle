import { Icon } from "./Icons";
import type { ReactNode } from "react";

type PageHeaderProps = {
  eyebrow?: string;
  title: string;
  description: string;
  actions?: ReactNode;
  icon?: "overview" | "today" | "performance" | "stability" | "learning" | "providers" | "operations" | "guide";
};

export function PageHeader({ eyebrow, title, description, actions, icon }: PageHeaderProps) {
  return (
    <section className="page-header">
      <div className="page-header__copy">
        {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
        <div className="page-header__title-row">
          {icon ? <Icon name={icon} className="page-header__icon" /> : null}
          <h2>{title}</h2>
        </div>
        <p className="page-header__description">{description}</p>
      </div>
      {actions ? <div className="page-header__actions">{actions}</div> : null}
    </section>
  );
}
