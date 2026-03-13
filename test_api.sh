#!/bin/bash

# IshemaLink API Testing Script
# Tests all major API endpoints

API_URL="http://localhost:8000/api"
TOKEN=""

echo "========================================"
echo "IshemaLink API Testing Script"
echo "========================================"
echo ""

# Test 1: Health Check
echo "1. Testing Health Check..."
curl -s "$API_URL/status/" | python -m json.tool
echo ""

# Test 2: API Root
echo "2. Testing API Root..."
curl -s "$API_URL/" | python -m json.tool
echo ""

# Test 3: User Registration
echo "3. Testing User Registration..."
RESPONSE=$(curl -s -X POST "$API_URL/auth/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser_'"$(date +%s)"'",
    "email": "test@ishemalink.com",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!",
    "phone": "+250788123456",
    "user_type": "CUSTOMER",
    "first_name": "Test",
    "last_name": "User"
  }')
echo "$RESPONSE" | python -m json.tool
echo ""

# Extract token if needed (would need actual token auth implementation)
# TOKEN=$(echo "$RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('token', ''))" 2>/dev/null || echo "")

# Test 4: NID Verification - Valid
echo "4. Testing NID Verification (Valid)..."
curl -s -X POST "$API_URL/auth/verify-nid/" \
  -H "Content-Type: application/json" \
  -d '{"nid": "1234567890123456"}' | python -m json.tool
echo ""

# Test 5: NID Verification - Invalid
echo "5. Testing NID Verification (Invalid)..."
curl -s -X POST "$API_URL/auth/verify-nid/" \
  -H "Content-Type: application/json" \
  -d '{"nid": "0123456789012345"}' | python -m json.tool
echo ""

# Test 6: List Shipments (requires token - will fail without auth)
echo "6. Testing Shipment List (requires authentication)..."
echo "Expected: 401 Unauthorized (authentication required)"
curl -s -X GET "$API_URL/shipments/" | python -m json.tool
echo ""

echo "========================================"
echo "Testing Complete!"
echo "========================================"
echo ""
echo "Notes:"
echo "- Tests 1-2: Health and API root (public)"
echo "- Tests 3-5: Registration and validation (public)"
echo "- Test 6: Shipments require token authentication"
echo ""
echo "To test authenticated endpoints:"
echo "1. Register a user and get token"
echo "2. Use token: curl -H 'Authorization: Token YOUR_TOKEN' ..."
echo ""
