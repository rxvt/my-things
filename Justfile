set quiet

# List available commands
default:
    just --list

# Run the test suite
test:
    uv run pytest tests/ -v

# Check for type errors
typecheck:
    uv run ty check

# Create a new spec file from template (e.g. just new-spec "add user auth")
new-spec name:
    #!/usr/bin/env bash
    set -euo pipefail
    mkdir -p specs
    last=$(ls specs/ 2>/dev/null | grep -oP '^\d+' | sort -n | tail -1)
    next=$(printf "%03d" $(( ${last:-0} + 1 )))
    slug=$(echo "{{ name }}" | tr '[:upper:]' '[:lower:]' | tr ' ' '_')
    file="specs/${next}_${slug}.md"
    title=$(echo "{{ name }}" | sed 's/./\U&/')
    cat > "$file" <<EOF
    # ${title}

    Status: draft

    ## Overview



    ## Requirements

    *
    EOF
    sed -i 's/^    //' "$file"
    echo "Created ${file}"
