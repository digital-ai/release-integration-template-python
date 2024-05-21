#!/bin/sh

MAX_WAIT_SECONDS=600
WAIT_INTERVAL=5

start_time=$(date +%s)
end_time=$((start_time + MAX_WAIT_SECONDS))

api_url="http://localhost:5516/api/v1/personal-access-tokens"
unique_id=$(date +%s%N | md5sum | awk '{print $1}')

while true; do
    current_time=$(date +%s)

    if [ $current_time -ge $end_time ]; then
        echo "Timeout reached. Exiting!"
        exit 1
    fi

    response=$(curl -s -i -X POST -u admin:admin -H "Content-Type: application/json;charset=UTF-8" -d '{"tokenNote": "'$unique_id'", "globalPermissions": ["runner#registration"]}' $api_url)

    if [ $? -ne 0 ]; then
        echo "Fetching token failed - probably still initializing... retrying soon"
        sleep $WAIT_INTERVAL
        continue
    fi

    http_status=$(echo "$response" | awk 'NR==1{print $2}')
    response_body=$(echo "$response" | sed -n '/^\r\{0,1\}$/,$p')
    if [ $http_status -ge 200 ] && [ $http_status -lt 300 ]; then
        echo "Successful fetched token..."
        export RELEASE_RUNNER_TOKEN=$(echo "$response_body" | jq -r '.token')
        break
    else
        echo "Fetching token - response had $http_status HTTP status code."
        echo "Response body was: $response_body"
    fi

    echo "Error fetching token! Waiting $WAIT_INTERVAL seconds before trying again..."
    sleep $WAIT_INTERVAL
done

exec /app/release-runner --profiles docker
