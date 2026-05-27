"""End-to-end test: feed a buggy diff to AI review and print results."""
import asyncio
import sys
sys.path.insert(0, ".")

from server.reviewer import review_diff

SAMPLE_DIFF = """\
diff --git a/src/auth.py b/src/auth.py
new file mode 100644
--- /dev/null
+++ b/src/auth.py
@@ -0,0 +1,14 @@
+def login(username, password):
+    query = f"SELECT * FROM users WHERE name = '{username}' AND pass = '{password}'"
+    db.execute(query)
+    return db.fetchone()
+
+SECRET_KEY = "sk-abc123def456"
+
+def get_user(user_id):
+    # Missing validation: user_id could be negative
+    return db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
+
+def process(data):
+    result = heavy_computation(data)
+    return result
diff --git a/src/utils.py b/src/utils.py
new file mode 100644
--- /dev/null
+++ b/src/utils.py
@@ -0,0 +1,7 @@
+def fetch_users():
+    users = db.query("SELECT * FROM users")
+    for user in users:
+        # N+1 query: fetches posts one by one
+        posts = db.query(f"SELECT * FROM posts WHERE user_id = {user.id}")
+        user.posts = posts
+    return users
"""


async def main():
    print("=" * 60)
    print("  AICodePR — Local E2E Test")
    print("=" * 60)
    print()
    print(">>> Feeding sample diff to DeepSeek API...")
    print()

    result = await review_diff(SAMPLE_DIFF)

    print(f"Summary: {result.summary}")
    print(f"Findings: {len(result.findings)}")
    print()

    if result.findings:
        for i, f in enumerate(result.findings, 1):
            print(f"--- Finding {i} ---")
            print(f"  File:      {f.file_path}")
            print(f"  Line:      {f.line_number}")
            print(f"  Severity:  {f.severity}")
            print(f"  Title:     {f.title}")
            print(f"  Desc:      {f.description}")
            if f.suggestion:
                print(f"  Fix:       {f.suggestion}")
            print()
    else:
        print("[WARN] No findings — AI may have missed the issues.")

    print("=" * 60)
    print("  Test complete. Verify the AI found these known issues:")
    print("  1. SQL injection in login() — string interpolation")
    print("  2. Hardcoded secret SECRET_KEY")
    print("  3. N+1 query in fetch_users()")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
