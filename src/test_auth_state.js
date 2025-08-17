// Test authentication state
console.log("=== Testing Authentication State ===");

// Check localStorage
console.log("1. localStorage contents:");
console.log("auth_token:", localStorage.getItem('auth_token'));
console.log("user_data:", localStorage.getItem('user_data'));

// Test API call with current token
async function testCurrentAuth() {
    const token = localStorage.getItem('auth_token');
    if (!token) {
        console.log("2. No token found in localStorage");
        return;
    }
    
    console.log("2. Testing API call with current token:", token.substring(0, 20) + "...");
    
    try {
        const response = await fetch('http://localhost:8000/api/v1/dashboard', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        console.log("3. API Response Status:", response.status);
        
        if (response.ok) {
            const data = await response.json();
            console.log("4. API Response Data:", data);
        } else {
            console.log("4. API Error:", await response.text());
        }
    } catch (error) {
        console.error("5. Network Error:", error);
    }
}

testCurrentAuth();

