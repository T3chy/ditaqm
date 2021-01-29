if [ $(curl -s -d "username=elam2" -d "password=bruh123" -X POST "127.0.0.1/api/register" | jq -r '.code') == 206 ]; then
	echo "b"
fi
