import type { ReactNode } from "react";

type KeyValue = {
  label: string;
  value: ReactNode;
};

export function KeyValueList({ items }: { items: KeyValue[] }) {
  return (
    <dl className="key-value-list">
      {items.map((item) => (
        <div key={item.label} className="key-value-list__row">
          <dt>{item.label}</dt>
          <dd>{item.value}</dd>
        </div>
      ))}
    </dl>
  );
}
