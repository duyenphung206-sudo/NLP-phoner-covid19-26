// Tạo nhãn (label), milestone và Issue từ file kế hoạch JSON trong thư mục plan/.
// Chạy bởi workflow .github/workflows/tao-issue-ke-hoach.yml (bấm "Run workflow" trong tab Actions).
// Chạy lại nhiều lần vẫn an toàn: Issue nào đã có (trùng tiêu đề) thì bỏ qua, không tạo trùng.

import { readFileSync, appendFileSync } from "node:fs";

const TOKEN = process.env.GITHUB_TOKEN;
const API = process.env.GITHUB_API_URL || "https://api.github.com";
const [OWNER, REPO] = (process.env.GITHUB_REPOSITORY || "/").split("/");
const FILE_KE_HOACH = process.env.KE_HOACH || "plan/tasks_bc1.json";
const FILE_TEAM = process.env.TEAM || "plan/team.json";
const CHAY_THU = (process.env.CHAY_THU || "false") === "true";
const NGHI_MS = Number(process.env.NGHI_MS ?? 700); // nghỉ giữa 2 lần tạo để tránh giới hạn tốc độ

const ngu = (ms) => new Promise((r) => setTimeout(r, ms));

async function goiApi(method, path, body) {
  const res = await fetch(`${API}${path}`, {
    method,
    headers: {
      Authorization: `Bearer ${TOKEN}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "nlp-de26-tao-issue",
      "Content-Type": "application/json",
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  const text = await res.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch { data = text; }
  return { status: res.status, data };
}

function taoNoiDung(t, usernames) {
  const tick = (t.xong_khi || []).map((x) => `- [ ] ${x}`).join("\n");
  const nguoi = t.nguoi.map((n, i) => (usernames[i] ? `${n} (@${usernames[i]})` : n)).join(", ");
  return [
    `**Người phụ trách:** ${nguoi}`,
    `**Thời gian:** ${t.bat_dau} → **${t.han}** · ước tính ${t.ngay_cong ? t.ngay_cong + " ngày công" : "—"}`,
    `**Gắn với:** ${t.gan_voi}`,
    "",
    "### Cần có trước (đầu vào)",
    t.dau_vao,
    "",
    "### Kết quả bàn giao (đầu ra)",
    t.dau_ra,
    "",
    "### ✅ Xong khi (tick từng ý khi đạt)",
    tick || "- [ ] (chưa có tiêu chí)",
    "",
    "---",
    "**Cập nhật tiến độ:** mỗi tối comment 3 dòng — *Đã xong / Mai làm / Đang vướng*.",
    `**Cách đóng Issue:** mở Pull Request có dòng \`Closes #<số của Issue này>\` → được review và merge thì Issue tự đóng.`,
    "",
    `<sub>Tạo tự động từ \`${FILE_KE_HOACH}\` · mã việc ${t.id}</sub>`,
  ].join("\n");
}

async function main() {
  if (!TOKEN || !OWNER || !REPO) throw new Error("Thiếu GITHUB_TOKEN hoặc GITHUB_REPOSITORY (script này chạy trong GitHub Actions).");
  const keHoach = JSON.parse(readFileSync(FILE_KE_HOACH, "utf8"));
  const team = JSON.parse(readFileSync(FILE_TEAM, "utf8")).thanh_vien || {};
  const tomTat = [];
  let soLoi = 0;
  console.log(`Repo: ${OWNER}/${REPO} · kế hoạch: ${FILE_KE_HOACH} · chạy thử: ${CHAY_THU}`);

  // 1) Nhãn
  for (const lb of keHoach.labels || []) {
    if (CHAY_THU) { console.log(`[thử] nhãn: ${lb.name}`); continue; }
    const r = await goiApi("POST", `/repos/${OWNER}/${REPO}/labels`, lb);
    if (r.status === 201) console.log(`+ nhãn ${lb.name}`);
    else if (r.status === 422) console.log(`= nhãn ${lb.name} (đã có)`);
    else { soLoi++; console.log(`! nhãn ${lb.name}: HTTP ${r.status} ${JSON.stringify(r.data)}`); }
  }

  // 2) Milestone
  let soMilestone = null;
  const ms = keHoach.milestone;
  if (ms) {
    const ds = await goiApi("GET", `/repos/${OWNER}/${REPO}/milestones?state=all&per_page=100`);
    const coSan = Array.isArray(ds.data) ? ds.data.find((m) => m.title === ms.title) : null;
    if (coSan) { soMilestone = coSan.number; console.log(`= milestone "${ms.title}" (#${soMilestone})`); }
    else if (CHAY_THU) console.log(`[thử] milestone: ${ms.title}`);
    else {
      const r = await goiApi("POST", `/repos/${OWNER}/${REPO}/milestones`, ms);
      if (r.status === 201) { soMilestone = r.data.number; console.log(`+ milestone "${ms.title}" (#${soMilestone})`); }
      else { soLoi++; console.log(`! milestone: HTTP ${r.status} ${JSON.stringify(r.data)}`); }
    }
  }

  // 3) Issue đã có (để không tạo trùng)
  const tieuDeDaCo = new Set();
  for (let page = 1; page < 50; page++) {
    const r = await goiApi("GET", `/repos/${OWNER}/${REPO}/issues?state=all&per_page=100&page=${page}`);
    if (!Array.isArray(r.data) || r.data.length === 0) break;
    for (const it of r.data) if (!it.pull_request) tieuDeDaCo.add(it.title);
    if (r.data.length < 100) break;
  }

  // 4) Tạo Issue
  for (const t of keHoach.tasks) {
    const usernames = t.nguoi.map((n) => (team[n] || "").trim().replace(/^@/, ""));
    const assignees = usernames.filter(Boolean);
    if (tieuDeDaCo.has(t.tieu_de)) {
      console.log(`= ${t.tieu_de} (đã có, bỏ qua)`);
      tomTat.push([t.id, t.tieu_de, "đã có"]);
      continue;
    }
    if (CHAY_THU) {
      console.log(`[thử] ${t.tieu_de} → ${assignees.join(", ") || "(chưa gán)"} · nhãn: ${t.nhan.join(", ")}`);
      tomTat.push([t.id, t.tieu_de, "chạy thử"]);
      continue;
    }
    const body = { title: t.tieu_de, body: taoNoiDung(t, usernames), labels: t.nhan, assignees };
    if (soMilestone) body.milestone = soMilestone;
    let r = await goiApi("POST", `/repos/${OWNER}/${REPO}/issues`, body);
    let ghiChu = "";
    if (r.status === 422 && assignees.length) {
      // Thường do username sai hoặc bạn đó chưa nhận lời mời vào repo -> tạo không gán người
      delete body.assignees;
      r = await goiApi("POST", `/repos/${OWNER}/${REPO}/issues`, body);
      ghiChu = " (chưa gán được người: kiểm tra plan/team.json và lời mời vào repo)";
    }
    if (r.status !== 201) {
      soLoi++;
      console.log(`! ${t.tieu_de}: HTTP ${r.status} ${JSON.stringify(r.data)}`);
      tomTat.push([t.id, t.tieu_de, `LỖI ${r.status}`]);
      continue;
    }
    const so = r.data.number;
    if (t.trang_thai === "Xong") {
      await goiApi("PATCH", `/repos/${OWNER}/${REPO}/issues/${so}`, { state: "closed", state_reason: "completed" });
      ghiChu += " · đã đóng vì việc đã xong trước";
    }
    console.log(`+ #${so} ${t.tieu_de}${ghiChu}`);
    tomTat.push([t.id, `#${so} ${t.tieu_de}`, "tạo mới" + ghiChu]);
    await ngu(NGHI_MS);
  }

  // 5) Tóm tắt hiện trên trang kết quả của workflow
  if (process.env.GITHUB_STEP_SUMMARY) {
    const md = ["### Kết quả tạo Issue", "", "| Mã | Issue | Kết quả |", "|---|---|---|",
      ...tomTat.map(([a, b, c]) => `| ${a} | ${b} | ${c} |`), "", `Số lỗi: **${soLoi}**`].join("\n");
    appendFileSync(process.env.GITHUB_STEP_SUMMARY, md + "\n");
  }
  if (soLoi > 0) { console.log(`Có ${soLoi} lỗi — đọc các dòng bắt đầu bằng "!" ở trên.`); process.exit(1); }
  console.log("Hoàn tất.");
}

main().catch((e) => { console.error(e); process.exit(1); });
