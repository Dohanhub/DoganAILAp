import React, { useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { CheckCircle2, ArrowRight, ArrowLeft, Smartphone, Activity, CreditCard, Upload, MessageSquare, Settings, User, Rocket, Shield, PlayCircle, Receipt } from "lucide-react";

// Minimal utility
const cx = (...c) => c.filter(Boolean).join(" ");

const steps = [
  { key: "welcome", title: "Welcome", icon: Rocket, desc: "Intro & quick tour" },
  { key: "signup", title: "Sign Up", icon: User, desc: "Create account" },
  { key: "intake", title: "Project Intake", icon: Upload, desc: "Provide details" },
  { key: "assistant", title: "AI Assistant", icon: MessageSquare, desc: "Guided setup" },
  { key: "review", title: "Review & Policy", icon: Shield, desc: "Check & approve" },
  { key: "payment", title: "Payment", icon: CreditCard, desc: "Complete order" },
  { key: "done", title: "Done", icon: CheckCircle2, desc: "Confirmation" },
] as const;

const variants = {
  enter: { opacity: 0, y: 12 },
  center: { opacity: 1, y: 0, transition: { duration: 0.25 } },
  exit: { opacity: 0, y: -12, transition: { duration: 0.18 } },
};

export default function DualScreenWorkflowSimulator() {
  const [stepIndex, setStepIndex] = useState(0);
  const [logs, setLogs] = useState<string[]>(["Simulator booted. Ready when you are ✨"]);
  const [compact, setCompact] = useState(false);

  // Fake user data for demo
  const [profile, setProfile] = useState({
    name: "Abu Omar",
    email: "abu.omar@example.com",
    company: "Dogan Hub",
  });
  const [intake, setIntake] = useState({
    goal: "Launch a customer-facing AI assistant",
    dataset: "Knowledge base PDFs",
    notes: "Arabic+English, tone: formal-warm",
  });
  const [policyAccepted, setPolicyAccepted] = useState(false);
  const [card, setCard] = useState({ number: "", name: "", cvv: "", exp: "" });

  const progress = useMemo(() => ((stepIndex + 1) / steps.length) * 100, [stepIndex]);

  const pushLog = (msg: string) => setLogs((l) => [timeStamp() + " " + msg, ...l].slice(0, 30));

  const next = () => {
    const s = steps[stepIndex];
    pushLog(`User completed step: ${s.title}`);
    if (stepIndex < steps.length - 1) setStepIndex(stepIndex + 1);
  };
  const back = () => setStepIndex((i) => Math.max(0, i - 1));

  return (
    <div className={cx("min-h-screen w-full p-4 md:p-6 lg:p-8", "bg-gradient-to-b from-slate-50 to-white")}> 
      <header className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <PlayCircle className="h-6 w-6" />
          <h1 className="text-xl md:text-2xl font-semibold">Dual-Screen Workflow Simulator</h1>
          <Badge variant="secondary" className="ml-1">demo</Badge>
        </div>
        <div className="flex items-center gap-4">
          <div className="hidden md:flex items-center gap-2 text-sm text-slate-500"><Activity className="h-4 w-4"/> Live mock</div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-500">Compact</span>
            <Switch checked={compact} onCheckedChange={setCompact} />
          </div>
        </div>
      </header>

      <div className={cx("grid gap-6", compact ? "grid-cols-1" : "grid-cols-1 lg:grid-cols-2")}>
        {/* Left: User mobile screen */}
        <Card className="shadow-lg">
          <CardHeader className="pb-2">
            <div className="flex items-center gap-3">
              <Smartphone className="h-5 w-5"/>
              <CardTitle className="text-base md:text-lg">User Screen (Mobile)</CardTitle>
            </div>
            <p className="text-xs text-slate-500">Simulates what the end-user taps, types, and sees.</p>
          </CardHeader>
          <CardContent>
            <div className="mx-auto w-full md:w-[360px]">
              <PhoneFrame>
                <StepIndicator stepIndex={stepIndex} />
                <div className="px-4 pb-4">
                  <Progress value={progress} className="h-2 my-3" />
                  <AnimatePresence mode="wait">
                    <motion.div key={steps[stepIndex].key} variants={variants} initial="enter" animate="center" exit="exit">
                      {stepIndex === 0 && (
                        <Welcome onNext={() => { pushLog("User started onboarding"); next(); }} />
                      )}
                      {stepIndex === 1 && (
                        <Signup profile={profile} setProfile={setProfile} onNext={() => { pushLog(`Signed up: ${profile.email}`); next(); }} onBack={back} />
                      )}
                      {stepIndex === 2 && (
                        <Intake intake={intake} setIntake={setIntake} onNext={() => { pushLog("Intake submitted"); next(); }} onBack={back} />
                      )}
                      {stepIndex === 3 && (
                        <Assistant intake={intake} onNext={() => { pushLog("Assistant configured a draft workflow"); next(); }} onBack={back} />
                      )}
                      {stepIndex === 4 && (
                        <Review policyAccepted={policyAccepted} setPolicyAccepted={setPolicyAccepted} onNext={() => { pushLog("Policies accepted"); next(); }} onBack={back} />
                      )}
                      {stepIndex === 5 && (
                        <Payment card={card} setCard={setCard} onNext={() => { pushLog("Payment authorized (mock)"); next(); }} onBack={back} />
                      )}
                      {stepIndex === 6 && (
                        <Done onRestart={() => { setStepIndex(0); pushLog("Restarted simulation"); }} />
                      )}
                    </motion.div>
                  </AnimatePresence>
                </div>
              </PhoneFrame>
            </div>
          </CardContent>
        </Card>

        {/* Right: System/team view */}
        <Card className="shadow-lg">
          <CardHeader className="pb-2">
            <div className="flex items-center gap-3">
              <Settings className="h-5 w-5"/>
              <CardTitle className="text-base md:text-lg">System & Team View</CardTitle>
            </div>
            <p className="text-xs text-slate-500">Shows the behind-the-scenes events as the user moves through the flow.</p>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="events">
              <TabsList className="mb-2">
                <TabsTrigger value="events">Event Log</TabsTrigger>
                <TabsTrigger value="state">State</TabsTrigger>
                <TabsTrigger value="journey">Journey Map</TabsTrigger>
              </TabsList>
              <TabsContent value="events">
                <div className="h-[420px] overflow-auto rounded-lg border bg-white p-3">
                  <ul className="space-y-2">
                    {logs.map((l, i) => (
                      <li key={i} className="text-sm text-slate-700 border-b pb-2 last:border-0">{l}</li>
                    ))}
                  </ul>
                </div>
              </TabsContent>
              <TabsContent value="state">
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <KV k="Step" v={`${stepIndex + 1} / ${steps.length} — ${steps[stepIndex].title}`} />
                  <KV k="User" v={profile.name} />
                  <KV k="Email" v={profile.email} />
                  <KV k="Company" v={profile.company} />
                  <KV k="Goal" v={intake.goal} />
                  <KV k="Dataset" v={intake.dataset} />
                  <KV k="Policy Accepted" v={policyAccepted ? "Yes" : "No"} />
                </div>
              </TabsContent>
              <TabsContent value="journey">
                <div className="grid gap-3">
                  {steps.map((s, i) => (
                    <div key={s.key} className={cx("flex items-center gap-3 rounded-xl border p-3", i <= stepIndex ? "bg-green-50/50 border-green-200" : "bg-slate-50 border-slate-200")}> 
                      <s.icon className={cx("h-4 w-4", i <= stepIndex ? "text-green-600" : "text-slate-400")} />
                      <div className="flex-1">
                        <div className="text-sm font-medium">{i + 1}. {s.title}</div>
                        <div className="text-xs text-slate-500">{s.desc}</div>
                      </div>
                      {i < stepIndex ? <Badge variant="secondary">done</Badge> : i === stepIndex ? <Badge>current</Badge> : <Badge variant="outline">next</Badge>}
                    </div>
                  ))}
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>

      <footer className="mt-6 text-xs text-slate-500">
        Pro tip: Toggle Compact to demo single-screen or expand to show dual view. All data here is mock-only.
      </footer>
    </div>
  );
}

function StepIndicator({ stepIndex }: { stepIndex: number }) {
  return (
    <div className="px-4 pt-4 flex items-center justify-between">
      <div className="text-sm font-medium">{steps[stepIndex].title}</div>
      <Badge variant="outline">{stepIndex + 1}/{steps.length}</Badge>
    </div>
  );
}

function PhoneFrame({ children }: { children: React.ReactNode }) {
  return (
    <div className="mx-auto w-full rounded-3xl border bg-white shadow-inner">
      <div className="h-8 rounded-t-3xl bg-slate-100 flex items-center justify-center text-[10px] text-slate-400">notch</div>
      <div className="min-h-[520px]">{children}</div>
      <div className="h-4 rounded-b-3xl bg-slate-100" />
    </div>
  );
}

function Welcome({ onNext }: { onNext: () => void }) {
  return (
    <div className="space-y-3">
      <h3 className="text-lg font-semibold">Welcome aboard 👋</h3>
      <p className="text-sm text-slate-600">This quick tour will simulate how a user gets from zero to hero in your app.</p>
      <ul className="text-sm list-disc pl-5 text-slate-600 space-y-1">
        <li>1–2 min end-to-end demo</li>
        <li>Dual-screen: user + system telemetry</li>
        <li>All copy and data are placeholders</li>
      </ul>
      <Button className="w-full mt-2" onClick={onNext}>Start the tour <ArrowRight className="ml-2 h-4 w-4"/></Button>
    </div>
  );
}

function Signup({ profile, setProfile, onNext, onBack }: any) {
  return (
    <div className="space-y-3">
      <div className="grid gap-2">
        <Input placeholder="Full name" value={profile.name} onChange={(e) => setProfile({ ...profile, name: e.target.value })} />
        <Input placeholder="Work email" type="email" value={profile.email} onChange={(e) => setProfile({ ...profile, email: e.target.value })} />
        <Input placeholder="Company" value={profile.company} onChange={(e) => setProfile({ ...profile, company: e.target.value })} />
      </div>
      <div className="flex gap-2">
        <Button variant="secondary" onClick={onBack}><ArrowLeft className="mr-2 h-4 w-4"/>Back</Button>
        <Button className="flex-1" onClick={onNext}>Continue <ArrowRight className="ml-2 h-4 w-4"/></Button>
      </div>
    </div>
  );
}

function Intake({ intake, setIntake, onNext, onBack }: any) {
  return (
    <div className="space-y-3">
      <Input placeholder="Primary goal" value={intake.goal} onChange={(e) => setIntake({ ...intake, goal: e.target.value })} />
      <Input placeholder="Main dataset" value={intake.dataset} onChange={(e) => setIntake({ ...intake, dataset: e.target.value })} />
      <Textarea rows={4} placeholder="Notes, tone, constraints" value={intake.notes} onChange={(e) => setIntake({ ...intake, notes: e.target.value })} />
      <div className="flex gap-2">
        <Button variant="secondary" onClick={onBack}><ArrowLeft className="mr-2 h-4 w-4"/>Back</Button>
        <Button className="flex-1" onClick={onNext}>Submit Intake <ArrowRight className="ml-2 h-4 w-4"/></Button>
      </div>
    </div>
  );
}

function Assistant({ intake, onNext, onBack }: any) {
  return (
    <div className="space-y-3">
      <div className="rounded-xl border p-3 bg-slate-50 text-sm">
        <div className="font-medium mb-1">Assistant Plan (auto-generated)</div>
        <ul className="list-disc pl-5 space-y-1 text-slate-600">
          <li>Set up knowledge connectors for: <b>{intake.dataset || "(dataset)"}</b></li>
          <li>Configure intents: Support, Sales, FAQ</li>
          <li>Language: Arabic + English, tone: formal-warm</li>
          <li>Guardrails: PII redaction, escalation to human</li>
        </ul>
      </div>
      <Button className="w-full" onClick={onNext}>Looks good <ArrowRight className="ml-2 h-4 w-4"/></Button>
      <Button variant="secondary" className="w-full" onClick={onBack}><ArrowLeft className="mr-2 h-4 w-4"/>Back</Button>
    </div>
  );
}

function Review({ policyAccepted, setPolicyAccepted, onNext, onBack }: any) {
  return (
    <div className="space-y-3">
      <div className="rounded-xl border p-3 bg-slate-50 text-sm">
        <div className="font-medium mb-1">Review & Policies</div>
        <p className="text-slate-600">Check our acceptable use, data processing addendum, and uptime policy. Toggle to accept.</p>
      </div>
      <div className="flex items-center justify-between rounded-xl border p-3">
        <div>
          <div className="text-sm font-medium">I accept the policies</div>
          <div className="text-xs text-slate-500">You can export a signed receipt on completion.</div>
        </div>
        <Switch checked={policyAccepted} onCheckedChange={setPolicyAccepted} />
      </div>
      <div className="flex gap-2">
        <Button variant="secondary" onClick={onBack}><ArrowLeft className="mr-2 h-4 w-4"/>Back</Button>
        <Button disabled={!policyAccepted} className="flex-1" onClick={onNext}>Proceed <ArrowRight className="ml-2 h-4 w-4"/></Button>
      </div>
    </div>
  );
}

function Payment({ card, setCard, onNext, onBack }: any) {
  return (
    <div className="space-y-3">
      <div className="grid gap-2">
        <Input placeholder="Cardholder name" value={card.name} onChange={(e) => setCard({ ...card, name: e.target.value })} />
        <Input placeholder="Card number" value={card.number} onChange={(e) => setCard({ ...card, number: e.target.value })} />
        <div className="grid grid-cols-2 gap-2">
          <Input placeholder="MM/YY" value={card.exp} onChange={(e) => setCard({ ...card, exp: e.target.value })} />
          <Input placeholder="CVV" value={card.cvv} onChange={(e) => setCard({ ...card, cvv: e.target.value })} />
        </div>
      </div>
      <Button className="w-full" onClick={onNext}><CreditCard className="mr-2 h-4 w-4"/> Pay SAR 199</Button>
      <Button variant="secondary" className="w-full" onClick={onBack}><ArrowLeft className="mr-2 h-4 w-4"/>Back</Button>
    </div>
  );
}

function Done({ onRestart }: { onRestart: () => void }) {
  return (
    <div className="space-y-3 text-center">
      <CheckCircle2 className="mx-auto h-10 w-10 text-green-600"/>
      <h3 className="text-lg font-semibold">You're all set</h3>
      <p className="text-sm text-slate-600">Your workspace is provisioned. A receipt is available in Settings → Billing.</p>
      <div className="flex flex-col gap-2">
        <Button className="w-full" onClick={onRestart}>Run again</Button>
        <Button variant="outline" className="w-full"><Receipt className="mr-2 h-4 w-4"/> Download mock receipt</Button>
      </div>
    </div>
  );
}

function KV({ k, v }: { k: string; v: string }) {
  return (
    <div className="rounded-lg border p-3 bg-white">
      <div className="text-[10px] uppercase tracking-wide text-slate-500">{k}</div>
      <div className="text-sm font-medium text-slate-800 truncate">{v}</div>
    </div>
  );
}

function timeStamp() {
  const d = new Date();
  const hh = String(d.getHours()).padStart(2, "0");
  const mm = String(d.getMinutes()).padStart(2, "0");
  const ss = String(d.getSeconds()).padStart(2, "0");
  return `[${hh}:${mm}:${ss}]`;
}
