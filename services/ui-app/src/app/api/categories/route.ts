import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  const res = await fetch("http://localhost:8000/categories");
  const data = await res.json();
  return NextResponse.json(data);
}
