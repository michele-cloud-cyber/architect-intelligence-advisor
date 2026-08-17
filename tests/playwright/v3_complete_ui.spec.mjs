import { test, expect } from "@playwright/test";

test("complete view exposes and uses both Code & Test Lab modules", async ({ page }) => {
  await page.goto(process.env.AIA_V3_URL || "http://127.0.0.1:8526/");
  await expect(page.getByText("3.0.0", { exact: true })).toBeVisible();
  await page.getByRole("tab", { name: "Code & Test Lab" }).click();

  await page.getByRole("tab", { name: "Code → Architecture & Risk" }).click();
  await expect(page.getByLabel("Incolla Terraform")).toBeVisible();
  await expect(page.getByText("Carica .tf o ZIP controllato")).toBeVisible();
  await page.getByRole("button", { name: "Analizza staticamente" }).click();
  await expect(page.getByText("Architettura visuale")).toBeVisible();
  await expect(page.getByText("Finding granulari")).toBeVisible();
  await expect(page.getByText("FinOps demo trasversale")).toBeVisible();

  await page.getByRole("tab", { name: "Vulnerability Intelligence" }).click();
  await expect(page.getByRole("heading", { name: "Vulnerability Intelligence" })).toBeVisible();
  await expect(page.getByText(/CVE\/CVSS sintetici/)).toBeVisible();
  await expect(page.getByText("CVE ID")).toBeVisible();
  await expect(page.getByText("CVSS vector")).toBeVisible();
  await expect(page.getByText("Mapping Terraform")).toBeVisible();
  await expect(page.getByText("Security Findings")).toBeVisible();
});
