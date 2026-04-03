import { Panel } from "../components/Panel";
import { PageHeader } from "../components/PageHeader";
import { DECISION_DEFINITIONS, GUIDE_SECTIONS, METRIC_DEFINITIONS } from "../lib/explain";

function DefinitionGrid({
  title,
  subtitle,
  items,
}: {
  title: string;
  subtitle: string;
  items: Array<{ label: string; meaning: string }>;
}) {
  return (
    <Panel title={title} subtitle={subtitle}>
      <div className="definition-grid">
        {items.map((item) => (
          <article key={item.label} className="definition-card">
            <p className="eyebrow">{item.label}</p>
            <p className="definition-card__body">{item.meaning}</p>
          </article>
        ))}
      </div>
    </Panel>
  );
}

export function GuidePage() {
  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Guide"
        title="How to use NBA Oracle"
        description="A product guide for reading the dashboard, understanding the metrics, and using the system for manual betting decisions."
        icon="guide"
      />
      <section className="guide-stack">
        {GUIDE_SECTIONS.map((section) => (
          <Panel key={section.title} title={section.title} subtitle={section.body}>
            <ul className="reason-list guide-points">
              {section.points.map((point) => (
                <li key={point}>{point}</li>
              ))}
            </ul>
          </Panel>
        ))}
      </section>
      <section className="panel-grid panel-grid--two">
        <DefinitionGrid
          title="Decision language"
          subtitle="These are the main call types you will see on the Today page."
          items={DECISION_DEFINITIONS}
        />
        <DefinitionGrid
          title="Metric glossary"
          subtitle="These metrics explain value, not just likely winners."
          items={METRIC_DEFINITIONS}
        />
      </section>
      <Panel
        title="Recommended daily workflow"
        subtitle="Use the dashboard in this order when you are making manual betting decisions."
      >
        <ol className="guide-flow">
          <li>Check Overview first to see whether the system is healthy or working with degraded inputs.</li>
          <li>Open Today and read the decision, summary sentence, EV, and Edge before thinking about a bet.</li>
          <li>Use Providers if you need to understand whether fallback or missing inputs are lowering confidence.</li>
          <li>Use Stability and Learning as trust signals, not as direct betting triggers.</li>
          <li>Use Operations only when you need to refresh or review the current backend state.</li>
        </ol>
      </Panel>
    </div>
  );
}
