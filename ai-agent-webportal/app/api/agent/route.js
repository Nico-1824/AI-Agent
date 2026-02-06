import { NextResponse } from "next/server";

export async function POST(req) {
  const { message } = await req.json();

  const r = await fetch("http://localhost:8000/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ input: message }),
  });

  const data = await r.json();
  return NextResponse.json(data, { status: r.status });
}
