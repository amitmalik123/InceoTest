// helper/global.auth.setup.spec.ts
import { test } from "@playwright/test";

test("create auth storage", async ({ page }) => {

  test.setTimeout(600000); 

  await page.goto("/");
  await page.fill("#okta-signin-username", process.env.USR_Global );
  await page.fill("#okta-signin-password", process.env.PASS_Global );
  await page.click("#okta-signin-submit");

    await page.waitForURL("**/dashboard", { timeout: 60000 });

  await page.context().storageState({ path: '.auth/user.json' });
  console.log("✅ Auth storage SAVED ");
});

