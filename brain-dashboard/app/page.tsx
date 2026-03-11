export default async function Home() {
  const status = await fetch('http://localhost:3000/api/status', { cache: 'no-store' }).then((r) => r.json()).catch(() => ({ ok: false }));
  return (
    <main style={{ padding: 24, fontFamily: 'sans-serif' }}>
      <h1>EvezOS Brain Dashboard</h1>
      <p>Real-time autonomous controller status.</p>
      <pre>{JSON.stringify(status, null, 2)}</pre>
    </main>
  );
}
