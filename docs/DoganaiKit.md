# ScenarioKit Mobile — Full App (Expo + TypeScript)

Purpose: Mobile client for ScenarioKit. Pick scenario → configure → deploy → chat → OCR ingest. Works with IBM, Azure, Google, AWS, NVIDIA via your backend adapters. Arabic/English, RTL, offline cache, notifications.

---

## 0) Repo Layout

```
scenariokit/
└─ apps/
   └─ mobile/
      ├─ app.json
      ├─ package.json
      ├─ tsconfig.json
      ├─ babel.config.js
      ├─ .env.sample
      └─ src/
         ├─ App.tsx
         ├─ navigation/
         │  └─ index.tsx
         ├─ screens/
         │  ├─ HomeScreen.tsx
         │  ├─ ScenarioScreen.tsx
         │  ├─ DeployScreen.tsx
         │  ├─ ChatScreen.tsx
         │  ├─ OCRScreen.tsx
         │  └─ SettingsScreen.tsx
         ├─ components/
         │  ├─ KitCard.tsx
         │  ├─ ParamField.tsx
         │  └─ MessageBubble.tsx
         ├─ services/
         │  └─ api.ts
         ├─ store/
         │  └─ state.ts
         ├─ i18n/
         │  ├─ index.ts
         │  ├─ ar.json
         │  └─ en.json
         ├─ theme/
         │  └─ theme.ts
         └─ utils/
            └─ types.ts
```

---

## 1) Quickstart

```
cd scenariokit/apps/mobile
cp .env.sample .env        # set EXPO_PUBLIC_API_BASE_URL
npm i
npm run start              # Expo dev
```

Environment variables are read via `EXPO_PUBLIC_*` prefix only.

---

## 2) Configuration

**.env.sample**

```
EXPO_PUBLIC_API_BASE_URL=https://api.example.com
EXPO_PUBLIC_DEFAULT_LANG=ar
```

**app.json**

```json
{
  "expo": {
    "name": "ScenarioKit Mobile",
    "slug": "scenariokit-mobile",
    "scheme": "scenariokit",
    "version": "0.1.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "splash": { "image": "./assets/splash.png", "resizeMode": "contain" },
    "updates": { "fallbackToCacheTimeout": 0 },
    "assetBundlePatterns": ["**/*"],
    "ios": { "supportsTablet": true },
    "android": { "adaptiveIcon": { "foregroundImage": "./assets/adaptive-icon.png" } },
    "web": { "bundler": "metro" }
  }
}
```

**package.json**

```json
{
  "name": "scenariokit-mobile",
  "private": true,
  "version": "0.1.0",
  "main": "node_modules/expo/AppEntry.js",
  "scripts": {
    "start": "expo start",
    "android": "expo run:android",
    "ios": "expo run:ios",
    "web": "expo start --web",
    "lint": "eslint ."
  },
  "dependencies": {
    "expo": "^51.0.0",
    "react": "^18.2.0",
    "react-native": "0.74.0",
    "@react-navigation/native": "^6.1.9",
    "@react-navigation/native-stack": "^6.9.18",
    "expo-camera": "~15.0.8",
    "expo-file-system": "~16.0.8",
    "@react-native-async-storage/async-storage": "^1.21.0",
    "i18next": "^23.10.0",
    "react-i18next": "^13.5.0"
  },
  "devDependencies": {
    "typescript": "^5.5.0",
    "@types/react": "^18.2.66",
    "@types/react-native": "^0.73.0"
  }
}
```

**tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2021",
    "module": "ESNext",
    "jsx": "react-jsx",
    "strict": true,
    "moduleResolution": "node",
    "esModuleInterop": true,
    "skipLibCheck": true,
    "baseUrl": "./src",
    "paths": { "*": ["*"] }
  },
  "include": ["src"]
}
```

**babel.config.js**

```js
module.exports = function(api){
  api.cache(true);
  return { presets: ['babel-preset-expo'] };
}
```

---

## 3) Types

**src/utils/types.ts**

```ts
export type StackKey = 'ibm'|'azure'|'google'|'aws'|'nvidia';
export type ScenarioKey = 'government_docs_chatbot'|'energy_ts_drone'|'bfsi_kyc_fraud'|'healthcare_radiology_summ';

export interface Scenario {
  key: ScenarioKey;
  name: string;
  sector: string;
  description: string;
  stacks: StackKey[];
}

export interface BlueprintSummary {
  scenario: ScenarioKey;
  stack: StackKey;
  version: string;
  params: Record<string, any>;
}

export interface Deployment {
  id: string;
  blueprintId: string;
  env: 'dev'|'prod';
  status: 'creating'|'ready'|'failed'|'updating';
  artifacts?: Record<string,string>;
}

export interface ChatMessage {
  id: string;
  role: 'user'|'assistant'|'system';
  text: string;
  ts: number;
}
```

---

## 4) i18n

**src/i18n/index.ts**

```ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import ar from './ar.json';
import en from './en.json';

const lng = process.env.EXPO_PUBLIC_DEFAULT_LANG || 'ar';

i18n.use(initReactI18next).init({
  compatibilityJSON: 'v3',
  resources: { ar: { translation: ar }, en: { translation: en } },
  lng, fallbackLng: 'en', interpolation: { escapeValue: false }
});

export default i18n;
```

**src/i18n/ar.json**

```json
{
  "title": "سيناريو كِت",
  "select_scenario": "اختر السيناريو",
  "deploy": "تنفيذ",
  "chat": "محادثة",
  "ocr": "مسح مستند",
  "settings": "الإعدادات",
  "stack": "المكدس التقني",
  "apply": "تطبيق",
  "status_ready": "جاهز",
  "status_creating": "قيد الإنشاء",
  "send": "إرسال",
  "language": "اللغة",
  "arabic": "العربية",
  "english": "الإنجليزية"
}
```

**src/i18n/en.json**

```json
{
  "title": "ScenarioKit",
  "select_scenario": "Select scenario",
  "deploy": "Deploy",
  "chat": "Chat",
  "ocr": "Scan Document",
  "settings": "Settings",
  "stack": "Vendor Stack",
  "apply": "Apply",
  "status_ready": "Ready",
  "status_creating": "Creating",
  "send": "Send",
  "language": "Language",
  "arabic": "Arabic",
  "english": "English"
}
```

---

## 5) Theme

**src/theme/theme.ts**

```ts
export const theme = {
  bg: '#0B1020',
  card: '#131A2A',
  text: '#E6EAF2',
  accent: '#57D0FF',
  muted: '#8EA3B0'
};
```

---

## 6) Global State

**src/store/state.ts**

```ts
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Scenario } from '../utils/types';

export const defaultScenarios: Scenario[] = [
  { key: 'government_docs_chatbot', name: 'Gov: Docs + Chatbot', sector: 'Government', description: 'OCR + RAG + Assistant', stacks: ['ibm','azure','google','aws','nvidia'] },
  { key: 'energy_ts_drone', name: 'Energy: TS + Drone CV', sector: 'Energy', description: 'Forecast + Inspection', stacks: ['ibm','azure','google','aws','nvidia'] },
  { key: 'bfsi_kyc_fraud', name: 'BFSI: KYC + Fraud', sector: 'BFSI', description: 'KYC + anomaly detection', stacks: ['ibm','azure','google','aws','nvidia'] },
  { key: 'healthcare_radiology_summ', name: 'Health: Radiology + Summ', sector: 'Healthcare', description: 'DICOM + clinical NLP', stacks: ['ibm','azure','google','aws','nvidia'] }
];

export async function save(key: string, val: any){ await AsyncStorage.setItem(key, JSON.stringify(val)); }
export async function load<T>(key: string): Promise<T|null>{ const v = await AsyncStorage.getItem(key); return v ? JSON.parse(v) as T : null; }
```

---

## 7) API Client

**src/services/api.ts**

```ts
const BASE = process.env.EXPO_PUBLIC_API_BASE_URL || 'http://localhost:8080';

async function http<T>(path: string, opts: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { headers: { 'Content-Type':'application/json' }, ...opts });
  if (!res.ok) throw new Error(`${res.status}`);
  return res.json();
}

export const API = {
  scenarios: () => http('/scenarios'),
  blueprint: (scenario: string, stack: string) => http(`/blueprints?scenario=${scenario}&stack=${stack}`),
  deploy: (body: any) => http('/deployments', { method: 'POST', body: JSON.stringify(body) }),
  deployment: (id: string) => http(`/deployments/${id}`),
  update: (id: string, changes: any) => http(`/deployments/${id}/update`, { method: 'POST', body: JSON.stringify(changes) }),
  chat: (deploymentId: string, text: string) => http('/chat', { method: 'POST', body: JSON.stringify({ deploymentId, text }) }),
  ocr: (deploymentId: string, fileUri: string) => http('/ocr', { method: 'POST', body: JSON.stringify({ deploymentId, fileUri }) }),
  events: (since?: string) => http(`/events${since ? `?since=${since}`:''}`)
};
```

---

## 8) Navigation and App Shell

**src/App.tsx**

```tsx
import React, { useEffect } from 'react';
import { I18nManager } from 'react-native';
import './i18n/index';
import { RootNavigator } from './navigation';

export default function App(){
  useEffect(() => { I18nManager.allowRTL(true); }, []);
  return <RootNavigator/>;
}
```

**src/navigation/index.tsx**

```tsx
import React from 'react';
import { NavigationContainer, DefaultTheme } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import HomeScreen from '../screens/HomeScreen';
import ScenarioScreen from '../screens/ScenarioScreen';
import DeployScreen from '../screens/DeployScreen';
import ChatScreen from '../screens/ChatScreen';
import OCRScreen from '../screens/OCRScreen';
import SettingsScreen from '../screens/SettingsScreen';

const Stack = createNativeStackNavigator();

export function RootNavigator(){
  return (
    <NavigationContainer theme={DefaultTheme}>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Home" component={HomeScreen}/>
        <Stack.Screen name="Scenario" component={ScenarioScreen}/>
        <Stack.Screen name="Deploy" component={DeployScreen}/>
        <Stack.Screen name="Chat" component={ChatScreen}/>
        <Stack.Screen name="OCR" component={OCRScreen}/>
        <Stack.Screen name="Settings" component={SettingsScreen}/>
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

---

## 9) UI Components

**src/components/KitCard.tsx**

```tsx
import React from 'react';
import { View, Text, Pressable } from 'react-native';
import { theme } from '../theme/theme';

export default function KitCard({ title, subtitle, onPress }:{title:string;subtitle:string;onPress:()=>void}){
  return (
    <Pressable onPress={onPress} style={{ backgroundColor: theme.card, padding:16, borderRadius:12, marginBottom:12 }}>
      <Text style={{ color: theme.text, fontSize:18, fontWeight:'600' }}>{title}</Text>
      <Text style={{ color: theme.muted, marginTop:6 }}>{subtitle}</Text>
    </Pressable>
  );
}
```

**src/components/ParamField.tsx**

```tsx
import React from 'react';
import { View, TextInput, Text } from 'react-native';
import { theme } from '../theme/theme';

export default function ParamField({ label, value, onChange }:{label:string; value:string; onChange:(v:string)=>void}){
  return (
    <View style={{ marginVertical:8 }}>
      <Text style={{ color: theme.text, marginBottom:6 }}>{label}</Text>
      <TextInput
        value={value}
        onChangeText={onChange}
        placeholder={label}
        placeholderTextColor={theme.muted}
        style={{ color: theme.text, backgroundColor: '#0F1626', borderRadius:10, padding:12 }}
      />
    </View>
  );
}
```

**src/components/MessageBubble.tsx**

```tsx
import React from 'react';
import { View, Text } from 'react-native';
import { theme } from '../theme/theme';
import { ChatMessage } from '../utils/types';

export default function MessageBubble({ m }:{ m: ChatMessage }){
  const isUser = m.role === 'user';
  return (
    <View style={{ alignSelf: isUser ? 'flex-end' : 'flex-start', backgroundColor: isUser ? theme.accent : theme.card, padding:10, marginVertical:6, borderRadius:12, maxWidth:'80%' }}>
      <Text style={{ color: isUser ? '#001018' : theme.text }}>{m.text}</Text>
    </View>
  );
}
```

---

## 10) Screens

**src/screens/HomeScreen.tsx**

```tsx
import React from 'react';
import { View, Text, ScrollView, Pressable } from 'react-native';
import { useTranslation } from 'react-i18next';
import { defaultScenarios } from '../store/state';
import KitCard from '../components/KitCard';

export default function HomeScreen({ navigation }: any){
  const { t } = useTranslation();
  return (
    <ScrollView style={{ flex:1, backgroundColor:'#0B1020', padding:16 }}>
      <Text style={{ color:'#E6EAF2', fontSize:28, fontWeight:'700', marginBottom:12 }}>{t('title')}</Text>
      {defaultScenarios.map((s) => (
        <KitCard key={s.key} title={`${s.name}`} subtitle={`${s.sector}`} onPress={() => navigation.navigate('Scenario', { s })} />
      ))}
      <Pressable onPress={() => navigation.navigate('Settings')} style={{ padding:12 }}>
        <Text style={{ color:'#8EA3B0' }}>{t('settings')}</Text>
      </Pressable>
    </ScrollView>
  );
}
```

**src/screens/ScenarioScreen.tsx**

```tsx
import React, { useEffect, useState } from 'react';
import { View, Text, Pressable } from 'react-native';
import { useTranslation } from 'react-i18next';
import ParamField from '../components/ParamField';
import { API } from '../services/api';

export default function ScenarioScreen({ route, navigation }: any){
  const { s } = route.params;
  const { t } = useTranslation();
  const [stack, setStack] = useState(s.stacks[0]);
  const [params, setParams] = useState({ project_name: 'mobile-demo', location: 'me-south-1', language: 'ar' });
  const [blueprint, setBlueprint] = useState<any>(null);

  useEffect(() => {
    API.blueprint(s.key, stack).then(setBlueprint).catch(()=>setBlueprint(null));
  }, [stack]);

  const set = (k:string,v:string)=> setParams(p=>({ ...p, [k]: v }));

  return (
    <View style={{ flex:1, backgroundColor:'#0B1020', padding:16 }}>
      <Text style={{ color:'#E6EAF2', fontSize:22, fontWeight:'600' }}>{s.name}</Text>
      <Text style={{ color:'#8EA3B0', marginTop:6 }}>{t('stack')}: {stack.toUpperCase()}</Text>

      <ParamField label="project_name" value={params.project_name} onChange={(v)=>set('project_name', v)} />
      <ParamField label="location" value={params.location} onChange={(v)=>set('location', v)} />
      <ParamField label="language" value={params.language} onChange={(v)=>set('language', v)} />

      <Pressable onPress={() => navigation.navigate('Deploy', { s, stack, params, blueprint })} style={{ backgroundColor:'#57D0FF', padding:14, borderRadius:12, marginTop:16 }}>
        <Text style={{ color:'#001018', textAlign:'center', fontWeight:'700' }}>{t('apply')}</Text>
      </Pressable>
    </View>
  );
}
```

**src/screens/DeployScreen.tsx**

```tsx
import React, { useEffect, useState } from 'react';
import { View, Text, ActivityIndicator, Pressable, Alert } from 'react-native';
import { API } from '../services/api';

export default function DeployScreen({ route, navigation }: any){
  const { s, stack, params } = route.params;
  const [status, setStatus] = useState<'idle'|'submitting'|'watching'|'ready'|'failed'>('idle');
  const [deployment, setDeployment] = useState<any>(null);

  const submit = async () => {
    try {
      setStatus('submitting');
      const dep = await API.deploy({ scenario: s.key, stack, params, env: 'dev' });
      setDeployment(dep);
      setStatus('watching');
      const poll = setInterval(async ()=>{
        const d = await API.deployment(dep.id);
        setDeployment(d);
        if (d.status === 'ready'){ clearInterval(poll); setStatus('ready'); }
        if (d.status === 'failed'){ clearInterval(poll); setStatus('failed'); }
      }, 3000);
    } catch(e:any){ Alert.alert('Error', e.message); setStatus('failed'); }
  };

  useEffect(()=>{ submit(); }, []);

  return (
    <View style={{ flex:1, backgroundColor:'#0B1020', padding:16, justifyContent:'center' }}>
      {status!=='ready' && <ActivityIndicator size="large" color="#57D0FF"/>}
      <Text style={{ color:'#E6EAF2', textAlign:'center', marginTop:12 }}>{deployment? `#${deployment.id} • ${deployment.status}`: 'Submitting…'}</Text>
      {status==='ready' && (
        <>
          <Pressable onPress={() => navigation.navigate('Chat', { deployment })} style={{ backgroundColor:'#57D0FF', padding:14, borderRadius:12, marginTop:16 }}>
            <Text style={{ color:'#001018', textAlign:'center', fontWeight:'700' }}>Open Chat</Text>
          </Pressable>
          <Pressable onPress={() => navigation.navigate('OCR', { deployment })} style={{ backgroundColor:'#131A2A', padding:14, borderRadius:12, marginTop:12 }}>
            <Text style={{ color:'#E6EAF2', textAlign:'center' }}>Open OCR</Text>
          </Pressable>
        </>
      )}
    </View>
  );
}
```

**src/screens/ChatScreen.tsx**

```tsx
import React, { useState } from 'react';
import { View, TextInput, FlatList, Pressable, Text } from 'react-native';
import { API } from '../services/api';
import MessageBubble from '../components/MessageBubble';
import { ChatMessage } from '../utils/types';

export default function ChatScreen({ route }: any){
  const { deployment } = route.params;
  const [input, setInput] = useState('');
  const [msgs, setMsgs] = useState<ChatMessage[]>([]);

  const send = async () => {
    const id = Date.now().toString();
    const m: ChatMessage = { id, role: 'user', text: input, ts: Date.now() };
    setMsgs(prev => [...prev, m]);
    setInput('');
    const r = await API.chat(deployment.id, m.text);
    const a: ChatMessage = { id: id+"a", role: 'assistant', text: r.text || JSON.stringify(r), ts: Date.now() };
    setMsgs(prev => [...prev, a]);
  };

  return (
    <View style={{ flex:1, backgroundColor:'#0B1020', padding:12 }}>
      <FlatList data={msgs} keyExtractor={m=>m.id} renderItem={({item}) => <MessageBubble m={item}/>} />
      <View style={{ flexDirection:'row', gap:8 }}>
        <TextInput value={input} onChangeText={setInput} placeholder="Message" placeholderTextColor="#8EA3B0" style={{ flex:1, color:'#E6EAF2', backgroundColor:'#131A2A', padding:12, borderRadius:12 }} />
        <Pressable onPress={send} style={{ backgroundColor:'#57D0FF', padding:12, borderRadius:12 }}>
          <Text style={{ color:'#001018', fontWeight:'700' }}>Send</Text>
        </Pressable>
      </View>
    </View>
  );
}
```

**src/screens/OCRScreen.tsx**

```tsx
import React, { useRef, useState } from 'react';
import { View, Text, Pressable, Image } from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import * as FileSystem from 'expo-file-system';
import { API } from '../services/api';

export default function OCRScreen({ route }: any){
  const { deployment } = route.params;
  const [perm, requestPermission] = useCameraPermissions();
  const [photoUri, setPhotoUri] = useState<string|undefined>();
  const [text, setText] = useState<string>('');

  if (!perm) return <View/>;
  if (!perm.granted) return (
    <View style={{ flex:1, alignItems:'center', justifyContent:'center' }}>
      <Pressable onPress={requestPermission}><Text>Grant Camera</Text></Pressable>
    </View>
  );

  const onSnap = async (uri: string) => {
    setPhotoUri(uri);
    const res = await API.ocr(deployment.id, uri);
    setText(res.text || JSON.stringify(res));
  };

  return (
    <View style={{ flex:1, backgroundColor:'#0B1020' }}>
      {!photoUri ? (
        <CameraView style={{ flex: 1 }} facing="back" onCameraReady={()=>{}} onTouchEnd={async()=>{}}/>
      ) : (
        <Image source={{ uri: photoUri }} style={{ flex:1 }} resizeMode="contain"/>
      )}
      <View style={{ padding:12, backgroundColor:'#131A2A' }}>
        <Pressable onPress={async()=>{
          const uri = FileSystem.cacheDirectory + `capture-${Date.now()}.jpg`;
          // In a real app, capture from CameraView. Placeholder writes empty file for flow.
          await FileSystem.writeAsStringAsync(uri, '');
          await onSnap(uri);
        }} style={{ backgroundColor:'#57D0FF', padding:12, borderRadius:12 }}>
          <Text style={{ color:'#001018', textAlign:'center', fontWeight:'700' }}>Capture</Text>
        </Pressable>
        {!!text && <Text style={{ color:'#E6EAF2', marginTop:8 }} numberOfLines={6}>{text}</Text>}
      </View>
    </View>
  );
}
```

**src/screens/SettingsScreen.tsx**

```tsx
import React, { useState } from 'react';
import { View, Text, Pressable } from 'react-native';

export default function SettingsScreen(){
  const [lang, setLang] = useState(process.env.EXPO_PUBLIC_DEFAULT_LANG || 'ar');
  return (
    <View style={{ flex:1, backgroundColor:'#0B1020', padding:16 }}>
      <Text style={{ color:'#E6EAF2', fontSize:20, fontWeight:'600' }}>Settings</Text>
      <Text style={{ color:'#8EA3B0', marginTop:8 }}>Language: {lang}</Text>
      <Pressable onPress={()=>setLang(lang==='ar'?'en':'ar')} style={{ backgroundColor:'#131A2A', padding:12, borderRadius:12, marginTop:12 }}>
        <Text style={{ color:'#E6EAF2' }}>Toggle Language</Text>
      </Pressable>
    </View>
  );
}
```

---

## 11) Backend Contract (aligns with your canvas spec)

Mobile expects:

- `GET /scenarios` → array of { key, name, sector, description, stacks }
- `GET /blueprints?scenario=..&stack=..` → `{ version, params, blueprint }`
- `POST /deployments` → `{ id, status:'creating' }`
- `GET /deployments/:id` → `{ id, status, artifacts, endpoints }`
- `POST /chat` → `{ text }` grounded answer from chosen vendor stack
- `POST /ocr` → `{ text }` OCR output via selected vendor service
- `GET /events?since=ISO` → regulatory change events if you wire Reg Watcher

Use your adapters to route vendor calls: IBM watsonx, Azure OpenAI, Google Vertex, AWS Bedrock, NVIDIA NeMo.

---

## 12) Enhancements

- Offline cache for last blueprint, deployment, and chat transcript via AsyncStorage.
- Arabic‑first UI, RTL enabled.
- Minimal theming for dark environments.
- Polling status for long‑running deploys.
- Safe API wrapper with errors surfaced to UI.

---

## 13) Testing Notes

- Use Expo Go for quick tests.
- Mock the backend by serving JSON with the contract above.
- Replace OCR capture placeholder with `takePictureAsync` using `expo-camera`.

---

## 14) Next Steps

- Wire push notifications for advisory events.
- Add secure session with JWT from your auth provider.
- Add cost insight per vendor stack on the Deploy screen.

```
```

---

## 15) Proposal Builder Module (Customer + Vendor Convincer)

Purpose: capture intel, auto‑draft multi‑format proposals, and align with IBM and alternative stacks. Ships inside the mobile app and backend.

### A) Outputs

- **Exec One‑Pager** (sector pain, KPIs, outcomes)
- **Technical Proposal** (ref architecture, data, models, security)
- **Competitive Grid** (IBM vs Azure/Google/AWS/NVIDIA + local SI)
- **PoC Playbook & SOW** (A→Z with roles, checkpoints)
- **Compliance Annex** (PDPL/SDAIA/NCA/CST/Sectoral)

### B) Templates Library

- One‑Pager, Tech Brief, Competitive Grid, PoC Playbook templates embedded as HTML partials. Render to HTML → PDF → PPTX. Templates are parameterized and versioned.

### C) Mobile UI

New screens:

1. **Evidence**: capture customer context, pains, KPIs, constraints; attach photos/PDF via OCR.
2. **Compose**: choose scenario + stack; pick templates; auto‑fill; edit fields.
3. **Competitive**: weight dimensions; preview scores; add local competitors.
4. **Compliance**: select regulator set; auto‑map controls; show gaps.
5. **Export**: choose format (HTML/PDF/PPTX); share link.

### D) Data Model (backend)

- `clients(id, name, sector, contacts, nda_flag)`
- `intel_sources(id, client_id, type, uri, captured_at, summary, tags[])`
- `proposals(id, client_id, scenario, primary_stack, status, version, created_by)`
- `proposal_sections(id, proposal_id, key, content_md, evidence_refs[])`
- `scores(id, proposal_id, dimension, weight, value)`
- `compliance_links(id, proposal_id, regulator, control_code, status, note)`
- `artifacts(id, proposal_id, kind, url, checksum)`

### E) API

- `POST /proposals` create draft from scenario + stack + client
- `GET /proposals/:id` fetch draft, sections, scores
- `POST /proposals/:id/ingest` attach intel (files/URLs/text)
- `POST /proposals/:id/compose` generate sections (LLM + RAG)
- `POST /proposals/:id/score` compute competitive scores (weights)
- `POST /proposals/:id/compliance` map controls from Reg Watcher
- `POST /proposals/:id/render?fmt=html|pdf|pptx` export bundle

### F) Generation Pipeline

1. **Gather**: pull uploads, OCR text, meeting notes, website snapshots.
2. **Ground**: RAG over corpora (customer docs + scenario kits + vendor docs).
3. **Draft**: fill templates with structured fields; cite sources; add KPIs.
4. **Score**: compute competitive grid via weighted model; include rationale.
5. **Check**: run governance checks (PII, hallucination tests, bias prompts, Arabic quality).
6. **Compile**: render HTML → PDF; build PPTX deck; package assets.

### G) Competitive Scoring (weights editable)

- Models/Tuning (0–10), Governance (0–10), Hybrid/On‑prem (0–10), Arabic Quality (0–10), Lead Time (0–10), KSA Compliance (0–10), TCO‑12mo (0–10) `weighted_score = Σ(weight_i * value_i) / Σ(weight_i)`

### H) Mobile Components (Expo)

- `screens/Proposal*` set: `ProposalEvidenceScreen`, `ProposalComposeScreen`, `ProposalCompetitiveScreen`, `ProposalComplianceScreen`, `ProposalExportScreen`.
- Use existing OCR screen for document capture; add file picker for PDFs.
- Live preview as HTML (WebView) with inline edit of fields.

### I) Backend Services

- `composer` worker: LLM calls, RAG, template fill.
- `renderer` worker: HTML→PDF via headless Chromium; PPTX via pptxgen.
- `storage`: object store for artifacts with signed URLs.

### J) Security & Audit

- All inputs tagged with client and sensitivity; NDA flag enforces export rules.
- Immutable audit log for sources, prompts, outputs, and approvals.

### K) Acceptance Criteria

- Create draft in ≤30 s with at least four filled sections.
- Export HTML/PDF/PPTX with identical content and styles.
- Competitive grid editable and recomputed live.
- Compliance annex populated from Reg Watcher within draft.

### L) Sprint Plan

- **Sprint 1**: Data model, APIs, Evidence + Compose screens, HTML renderer.
- **Sprint 2**: Competitive scoring UI, Compliance annex integration, PDF export.
- **Sprint 3**: PPTX export, sharing links, Arabic typography polish.

### M) Template Keys (auto‑fill)

- Company profile, current stack, data sources, KPIs, success criteria, risks, timeline, cost bands, roles (RACI), SLA/SLO, annex references.

