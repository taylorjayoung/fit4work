
    #!/bin/sh
    sed -i 's/sk-ant-api03-[A-Za-z0-9_-]\{40,\}/YOUR_ANTHROPIC_API_KEY/g' "$@"
    