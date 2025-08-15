// Test authentication flow
console.log("=== Testing Authentication Flow ===");

// Check localStorage
console.log("1. Checking localStorage:");
console.log("auth_token:", localStorage.getItem('auth_token'));
console.log("user_data:", localStorage.getItem('user_data'));

// Test API call
async function testAuthFlow() {
    try {
        const response = await fetch('http://localhost:8000/api/v1/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: 'dl1@gmail.com',
                password: 'SecurePassword123!'
            })
        });

        const data = await response.json();
        console.log("2. API Response:", data);

        if (data.data && data.data.access_token) {
            // Simulate what the UI should do
            localStorage.setItem('auth_token', data.data.access_token);
            localStorage.setItem('user_data', JSON.stringify(data.data.user));
            
            console.log("3. After setting localStorage:");
            console.log("auth_token:", localStorage.getItem('auth_token'));
            console.log("user_data:", localStorage.getItem('user_data'));
            
            // Test dashboard access
            const dashboardResponse = await fetch('http://localhost:8000/api/v1/dashboard', {
                headers: {
                    'Authorization': `Bearer ${data.data.access_token}`
                }
            });
            
            console.log("4. Dashboard Response Status:", dashboardResponse.status);
            if (dashboardResponse.ok) {
                const dashboardData = await dashboardResponse.json();
                console.log("Dashboard Data:", dashboardData);
            } else {
                console.log("Dashboard Error:", await dashboardResponse.text());
            }
        }
    } catch (error) {
        console.error("Error:", error);
    }
}

testAuthFlow();
