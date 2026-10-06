import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Save, Sparkles } from "lucide-react";

import { PageHeader } from "@/components/shared/PageHeader";
import {
  getAgentConfig,
  updateAgentConfig,
  type AgentConfigPayload,
  VOICE_OPTIONS,
  PERSONALITY_OPTIONS,
} from "@/lib/api/university";
import { usePermissions } from "@/lib/hooks/usePermissions";

export const Route = createFileRoute("/app/voice-agent")({
  head: () => ({
    meta: [
      { title: "Voice Agent — Scholaria" },
      {
        name: "description",
        content:
          "Configure your university's AI voice agent: voice, personality, greeting, and capabilities.",
      },
    ],
  }),
  component: VoiceAgentPage,
});

const voiceIds = new Set(VOICE_OPTIONS.map((v) => v.id));

const personalityLabels: Record<string, string> = {
  friendly: "Warm & welcoming",
  professional: "Quick & efficient",
  casual: "Playful & casual",
  formal: "Polished & formal",
  enthusiastic: "Energetic & enthusiastic",
};

function VoiceAgentPage() {
  const { canConfigureVoiceAgent } = usePermissions();
  const canEdit = canConfigureVoiceAgent();

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);

  const [agentName, setAgentName] = useState("Assistant");
  const [voiceId, setVoiceId] = useState(VOICE_OPTIONS[0].id);
  const [speed, setSpeed] = useState(1.0);
  const [personality, setPersonality] = useState("friendly");
  const [greetingMessage, setGreetingMessage] = useState(
    "Hello! Welcome to our university. How can I help you today?",
  );
  const [specialInstructions, setSpecialInstructions] = useState("");
  const [enableAdmissions, setEnableAdmissions] = useState(true);
  const [enableCourses, setEnableCourses] = useState(true);
  const [enableScholarships, setEnableScholarships] = useState(true);
  const [enableFaq, setEnableFaq] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        setIsLoading(true);
        const config = await getAgentConfig();
        setAgentName(config.agent_name);
        setPersonality(config.personality);
        setGreetingMessage(config.greeting_message);
        setSpecialInstructions(config.special_instructions || "");
        const configuredVoiceId = config.voice_config?.voice_id;
        setVoiceId(
          configuredVoiceId && voiceIds.has(configuredVoiceId)
            ? configuredVoiceId
            : VOICE_OPTIONS[0].id,
        );
        setSpeed(config.voice_config?.speed ?? 1.0);
        setEnableAdmissions(config.enable_admissions);
        setEnableCourses(config.enable_courses);
        setEnableScholarships(config.enable_scholarships);
        setEnableFaq(config.enable_faq);
      } catch (error) {
        // 404 -> no config yet, keep defaults
        if (!(error instanceof Error && error.message.startsWith("404:"))) {
          console.error("Failed to load agent config", error);
        }
      } finally {
        setIsLoading(false);
      }
    };
    load();
  }, []);

  const handleSave = async () => {
    try {
      setIsSaving(true);
      setSaveError(null);
      setSaveSuccess(null);

      const clampedSpeed = Math.min(2, Math.max(0.5, speed));
      const payload: AgentConfigPayload = {
        agent_name: agentName.trim() || "Assistant",
        personality,
        greeting_message: greetingMessage.trim(),
        special_instructions: specialInstructions.trim() || undefined,
        voice_config: {
          voice_id: voiceId,
          speed: clampedSpeed,
          language: "en",
        },
        enable_admissions: enableAdmissions,
        enable_courses: enableCourses,
        enable_scholarships: enableScholarships,
        enable_faq: enableFaq,
      };

      // updateAgentConfig upserts on the backend
      await updateAgentConfig(payload);
      setSaveSuccess("Agent settings saved.");
    } catch (error) {
      setSaveError(error instanceof Error ? error.message : "Failed to save agent settings");
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="mx-auto max-w-[1200px] px-4 py-6 lg:px-8 lg:py-8">
        <div className="text-center text-muted-foreground">Loading configuration...</div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-[1200px] px-4 py-6 lg:px-8 lg:py-8">
      <PageHeader
        title="Voice Agent"
        description="Configure how your university's AI agent greets and assists callers."
        actions={
          canEdit ? (
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="inline-flex h-9 items-center gap-2 rounded-md bg-gradient-primary px-3.5 text-sm font-semibold text-primary-foreground shadow-card transition-smooth hover:shadow-elevated disabled:opacity-60"
            >
              <Save className="h-4 w-4" />
              {isSaving ? "Saving..." : "Save changes"}
            </button>
          ) : undefined
        }
      />

      {saveError ? (
        <div className="mb-4 rounded-lg border border-destructive bg-destructive/10 p-3 text-sm text-destructive">
          {saveError}
        </div>
      ) : saveSuccess ? (
        <div className="mb-4 rounded-lg border border-success bg-success/10 p-3 text-sm text-success">
          {saveSuccess}
        </div>
      ) : null}

      {!canEdit && (
        <div className="mb-4 rounded-lg bg-muted p-3 text-sm text-muted-foreground">
          You have view-only access. Contact an owner to change the voice agent configuration.
        </div>
      )}

      <div className="mb-6 flex items-start gap-4 rounded-xl border border-border-subtle bg-gradient-surface p-5 shadow-card">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-primary shadow-glow">
          <Sparkles className="h-6 w-6 text-primary-foreground" />
        </div>
        <div>
          <h3 className="text-base font-semibold">{agentName || "University Voice Agent"}</h3>
          <p className="mt-0.5 text-sm text-muted-foreground">
            Handles questions about admissions, courses, scholarships, and FAQs.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        <Section title="Voice & Personality" subtitle="How your agent sounds.">
          <Field label="Agent name">
            <input
              className="input"
              value={agentName}
              disabled={!canEdit}
              onChange={(e) => setAgentName(e.target.value)}
            />
          </Field>
          <Field label="Personality">
            <select
              className="select"
              value={personality}
              disabled={!canEdit}
              onChange={(e) => setPersonality(e.target.value)}
            >
              {PERSONALITY_OPTIONS.map((p) => (
                <option key={p} value={p}>
                  {personalityLabels[p] ?? p}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Voice">
            <select
              className="select"
              value={voiceId}
              disabled={!canEdit}
              onChange={(e) => setVoiceId(e.target.value)}
            >
              {Object.entries(
                VOICE_OPTIONS.reduce<Record<string, typeof VOICE_OPTIONS>>((acc, v) => {
                  (acc[v.group] ??= []).push(v);
                  return acc;
                }, {}),
              ).map(([group, options]) => (
                <optgroup key={group} label={group}>
                  {options.map((o) => (
                    <option key={o.id} value={o.id}>
                      {o.label}
                    </option>
                  ))}
                </optgroup>
              ))}
            </select>
          </Field>
          <Field label="Speaking speed">
            <div className="mb-1 flex justify-between text-xs text-muted-foreground">
              <span>0.5x</span>
              <span>{speed.toFixed(2)}x</span>
              <span>2.0x</span>
            </div>
            <input
              type="range"
              min={0.5}
              max={2}
              step={0.05}
              value={speed}
              disabled={!canEdit}
              onChange={(e) => setSpeed(Number(e.target.value))}
              className="w-full accent-primary"
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Slow</span>
              <span>Normal</span>
              <span>Fast</span>
            </div>
          </Field>
        </Section>

        <Section title="Conversation" subtitle="Greeting and behavior.">
          <Field label="Greeting message">
            <textarea
              className="textarea min-h-28"
              value={greetingMessage}
              disabled={!canEdit}
              onChange={(e) => setGreetingMessage(e.target.value)}
            />
          </Field>
          <Field label="Special instructions">
            <textarea
              className="textarea min-h-32"
              value={specialInstructions}
              disabled={!canEdit}
              onChange={(e) => setSpecialInstructions(e.target.value)}
              placeholder="Additional guidance for how the agent should respond."
            />
          </Field>
        </Section>

        <Section title="Capabilities" subtitle="Topics the agent can handle.">
          <ToggleRow
            label="Enable admissions"
            checked={enableAdmissions}
            disabled={!canEdit}
            onChange={setEnableAdmissions}
          />
          <ToggleRow
            label="Enable courses"
            checked={enableCourses}
            disabled={!canEdit}
            onChange={setEnableCourses}
          />
          <ToggleRow
            label="Enable scholarships"
            checked={enableScholarships}
            disabled={!canEdit}
            onChange={setEnableScholarships}
          />
          <ToggleRow
            label="Enable FAQ"
            checked={enableFaq}
            disabled={!canEdit}
            onChange={setEnableFaq}
          />
        </Section>
      </div>

      <style>{`
        .select, .input, .textarea {
          width: 100%;
          padding: 0.5rem 0.75rem;
          border-radius: 0.375rem;
          border: 1px solid var(--color-border);
          background: var(--color-background);
          font-size: 0.875rem;
          transition: all 0.2s;
        }
        .textarea { resize: vertical; }
        .select:focus, .input:focus, .textarea:focus {
          outline: none;
          box-shadow: 0 0 0 2px var(--color-ring);
          border-color: transparent;
        }
        .input:disabled, .select:disabled, .textarea:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  );
}

function Section({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}) {
  return (
    <section className="space-y-4 rounded-xl border border-border-subtle bg-surface p-5 shadow-card">
      <div>
        <h3 className="font-semibold">{title}</h3>
        {subtitle && <p className="mt-0.5 text-xs text-muted-foreground">{subtitle}</p>}
      </div>
      {children}
    </section>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="space-y-1.5">
      <label className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        {label}
      </label>
      {children}
    </div>
  );
}

function ToggleRow({
  label,
  checked,
  disabled,
  onChange,
}: {
  label: string;
  checked: boolean;
  disabled?: boolean;
  onChange: (value: boolean) => void;
}) {
  return (
    <label
      className={
        "flex items-center justify-between py-1 " +
        (disabled ? "cursor-not-allowed opacity-70" : "cursor-pointer")
      }
    >
      <span className="text-sm">{label}</span>
      <span className="relative">
        <input
          type="checkbox"
          checked={checked}
          disabled={disabled}
          onChange={(e) => onChange(e.target.checked)}
          className="peer sr-only"
        />
        <span className="block h-5 w-9 rounded-full bg-muted transition-smooth peer-checked:bg-primary" />
        <span className="absolute left-0.5 top-0.5 h-4 w-4 rounded-full bg-surface shadow-card transition-smooth peer-checked:translate-x-4" />
      </span>
    </label>
  );
}
