import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  const ids = req.nextUrl.searchParams.get("ids");
  const category = req.nextUrl.searchParams.get("category");
  let url = "http://localhost:8000/vendors";
  if (ids) url += `?ids=${encodeURIComponent(ids)}`;
  else if (category) url += `?category=${encodeURIComponent(category)}`;
  const res = await fetch(url);
  const data = await res.json();
  return NextResponse.json(data);
}
