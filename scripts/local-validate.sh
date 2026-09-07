#!/bin/bash
set -e

IMAGE_NAME="agoraowl-validator"
ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)

echo "--- Building local validation image ($IMAGE_NAME) ---"
docker build -t "$IMAGE_NAME" -f "$ROOT_DIR/Dockerfile" "$ROOT_DIR"

# Helper function to run docker avoiding path conversion on Windows (Git Bash)
docker_run() {
    # MSYS_NO_PATHCONV=1 prevents Git Bash from transforming "/app" into "C:/Program Files/Git/app"
    MSYS_NO_PATHCONV=1 docker run --rm -v "$ROOT_DIR:/app" "$IMAGE_NAME" "$@"
}

echo -e "\n--- 🚀 Running syntax validation (scripts/check_rdf.py) ---"
docker_run python3 /app/scripts/check_rdf.py

echo -e "\n--- 🚀 Running SHACL validation (scripts/validate_shacl.py) ---"
docker_run python3 /app/scripts/validate_shacl.py

echo -e "\n--- 🚀 Running OWL 2 DL profile validation (ROBOT) ---"
LATEST_DL=$(ls -d "$ROOT_DIR/src"/*/ 2>/dev/null | xargs -n 1 basename | grep -E '^[0-9]+\.[0-9]+\.[0-9]+$' | sort -V | tail -n 1)
docker_run java -jar /opt/robot/robot.jar validate-profile --profile DL \
        --input "/app/src/$LATEST_DL/AgoraOWL.ttl" --output /tmp/dl-core.txt
if [ -f "$ROOT_DIR/src/$LATEST_DL/alignment.ttl" ]; then
  docker_run java -jar /opt/robot/robot.jar merge \
        --input "/app/src/$LATEST_DL/AgoraOWL.ttl" \
        --input "/app/src/$LATEST_DL/alignment.ttl" \
        validate-profile --profile DL --output /tmp/dl-merged.txt
fi

echo -e "\n--- 🚀 Running conformance suite (positives AND negatives) ---"
docker_run env AGORAOWL_ROBOT_JAR=/opt/robot/robot.jar python3 /app/scripts/conformance_suite.py

echo -e "\n--- 🚀 Running OWL consistency validation (ROBOT) ---"
# Find latest version folder for ROBOT (which still needs the manual catalog for now)
LATEST_VERSION=$(ls -d "$ROOT_DIR/src"/*/ 2>/dev/null | xargs -n 1 basename | grep -E '^[0-9]+\.[0-9]+\.[0-9]+$' | sort -V | tail -n 1)
LATEST_PATH="src/$LATEST_VERSION"

cat > "$ROOT_DIR/robot-catalog.xml" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<catalog xmlns="urn:oasis:names:tc:entity:xmlns:xml:catalog" prefer="public">
  <uri name="https://w3id.org/AgoraOWL/" uri="file:/app/$LATEST_PATH/AgoraOWL.ttl"/>
</catalog>
EOF

docker_run java -jar /opt/robot/robot.jar reason \
        --catalog /app/robot-catalog.xml \
        --input /app/$LATEST_PATH/examples/test-consistency.ttl \
        --reasoner ELK \
        --output /tmp/agoraowl-reasoned.owl

echo -e "\n--- 🚀 Running OWL consistency validation (ROBOT) on EO examples ---"
docker_run java -jar /opt/robot/robot.jar reason \
        --catalog /app/robot-catalog.xml \
        --input /app/$LATEST_PATH/examples/eo-instances.ttl \
        --reasoner ELK \
        --output /tmp/agoraowl-reasoned-eo.owl

rm "$ROOT_DIR/robot-catalog.xml"

echo -e "\n✅ All local validations completed successfully!"
