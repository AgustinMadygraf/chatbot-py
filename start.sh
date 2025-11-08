diff --git a/start.sh b/start.sh
new file mode 100755
index 0000000000000000000000000000000000000000..8449aaaed4f29849b350d9f1ed0e22eed37a0561
--- /dev/null
+++ b/start.sh
@@ -0,0 +1,18 @@
+#!/bin/sh
+set -euo pipefail
+
+rasa run \
+  --enable-api \
+  --cors "*" \
+  --model rasa_project/models \
+  --port 5005 \
+  --debug \
+  &
+rasa run actions \
+  --actions rasa_project.actions.actions \
+  --port 5055 \
+  &
+uvicorn main:app \
+  --host 0.0.0.0 \
+  --port 8080 \
+  --proxy-headers
