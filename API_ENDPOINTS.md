# Social Clones API Documentation

Base URL: `http://127.0.0.1:8000/v1`

---

## Authentication

### 1. Register User
```bash
curl -X POST http://127.0.0.1:8000/v1/auth/users/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Password123!","full_name":"John Doe"}'
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe"
}
```

---

### 2. Login (Get Tokens)
```bash
curl -X POST http://127.0.0.1:8000/v1/auth/token/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Password123!"}'
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGci...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGci..."
}
```

---

### 3. Refresh Token
```bash
curl -X POST http://127.0.0.1:8000/v1/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"eyJ0eXAiOiJKV1QiLCJhbGci..."}'
```

---

### 4. Get Current User
```bash
curl -X GET http://127.0.0.1:8000/v1/auth/me/ \
  -H "Authorization: Bearer <access_token>"
```

---

## How to Use Auth Token

### Step 1: Login to get tokens
```bash
curl -X POST http://127.0.0.1:8000/v1/auth/token/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"Password123!"}'
```

### Step 2: Copy the `access` token from response

### Step 3: Use it in Authorization header for private endpoints
```bash
curl -X GET http://127.0.0.1:8000/v1/auth/me/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGci..."
```

---

## Sample Users (after populate_data)

| Email | Password |
|-------|----------|
| alice@example.com | Password123! |
| bob@example.com | Password123! |
| charlie@example.com | Password123! |

---

# AMAZON CLONE

Base: `/v1/amazon`

## Public Endpoints

### Categories
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/categories/` | List all categories |
| GET | `/categories/{id}/` | Get category detail |

```bash
# List categories
curl http://127.0.0.1:8000/v1/amazon/categories/

# Get category by ID
curl http://127.0.0.1:8000/v1/amazon/categories/{category_id}/
```

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/products/` | List products |
| GET | `/products/{id}/` | Get product detail |
| GET | `/products/{id}/images/` | Get product images |
| GET | `/products/{id}/similar/` | Get similar products |

```bash
# List all products
curl http://127.0.0.1:8000/v1/amazon/products/

# Filter products
curl "http://127.0.0.1:8000/v1/amazon/products/?category=electronics&price_min=50000"

# Get product
curl http://127.0.0.1:8000/v1/amazon/products/{product_id}/

# Search products
curl "http://127.0.0.1:8000/v1/amazon/products/?q=macbook"
```

---

## Private Endpoints (Require Auth)

### Addresses
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/me/addresses/` | List my addresses |
| POST | `/me/addresses/` | Add address |
| PATCH | `/me/addresses/{id}/` | Update address |
| DELETE | `/me/addresses/{id}/` | Delete address |
| POST | `/me/addresses/{id}/default/` | Set default address |

```bash
# List addresses
curl http://127.0.0.1:8000/v1/amazon/me/addresses/ \
  -H "Authorization: Bearer <token>"

# Add address
curl -X POST http://127.0.0.1:8000/v1/amazon/me/addresses/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "line1": "123 Main St",
    "city": "New York",
    "postal_code": "10001",
    "country": "USA"
  }'
```

### Cart
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/me/cart/` | Get my cart |
| POST | `/me/cart/items/` | Add item to cart |
| PATCH | `/me/cart/items/{id}/` | Update item quantity |
| DELETE | `/me/cart/items/{id}/` | Remove item |
| DELETE | `/me/cart/` | Clear cart |

```bash
# Get cart
curl http://127.0.0.1:8000/v1/amazon/me/cart/ \
  -H "Authorization: Bearer <token>"

# Add item to cart
curl -X POST http://127.0.0.1:8000/v1/amazon/me/cart/items/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"productId": "<product_uuid>", "quantity": 2}'

# Update quantity
curl -X PATCH http://127.0.0.1:8000/v1/amazon/me/cart/items/{item_id}/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"quantity": 5}'

# Remove item
curl -X DELETE http://127.0.0.1:8000/v1/amazon/me/cart/items/{item_id}/ \
  -H "Authorization: Bearer <token>"
```

### Wishlist
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/me/wishlist/` | List wishlist |
| POST | `/me/wishlist/` | Add to wishlist |
| DELETE | `/me/wishlist/{id}/` | Remove from wishlist |
| GET | `/me/wishlist/check/` | Check if product in wishlist |

```bash
# Get wishlist
curl http://127.0.0.1:8000/v1/amazon/me/wishlist/ \
  -H "Authorization: Bearer <token>"

# Add to wishlist
curl -X POST http://127.0.0.1:8000/v1/amazon/me/wishlist/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"productId": "<product_uuid>"}'
```

### Orders
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/orders/` | List my orders |
| POST | `/orders/` | Create order |
| GET | `/orders/{id}/` | Get order detail |
| POST | `/orders/{id}/cancel/` | Cancel order |

```bash
# List orders
curl http://127.0.0.1:8000/v1/amazon/orders/ \
  -H "Authorization: Bearer <token>"

# Create order (requires addressId)
curl -X POST http://127.0.0.1:8000/v1/amazon/orders/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"addressId": "<address_uuid>", "paymentProvider": "stripe"}'

# Get order
curl http://127.0.0.1:8000/v1/amazon/orders/{order_id}/ \
  -H "Authorization: Bearer <token>"

# Cancel order
curl -X POST http://127.0.0.1:8000/v1/amazon/orders/{order_id}/cancel/ \
  -H "Authorization: Bearer <token>"
```

### Reviews
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/products/{id}/reviews/` | List reviews |
| POST | `/products/{id}/reviews/` | Add review |
| GET | `/reviews/{id}/` | Get review |
| PATCH | `/reviews/{id}/` | Update review |
| DELETE | `/reviews/{id}/` | Delete review |

```bash
# Add review
curl -X POST http://127.0.0.1:8000/v1/amazon/products/{product_id}/reviews/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"rating": 5, "title": "Great!", "body": "Loved it!"}'
```

---

## Admin Endpoints

```bash
# Get sales metrics
curl http://127.0.0.1:8000/v1/amazon/admin/metrics/sales/ \
  -H "Authorization: Bearer <admin_token>"

# Get top products
curl http://127.0.0.1:8000/v1/amazon/admin/metrics/top_products/ \
  -H "Authorization: Bearer <admin_token>"

# List inventory
curl http://127.0.0.1:8000/v1/amazon/inventory/ \
  -H "Authorization: Bearer <admin_token>"

# Update inventory
curl -X PATCH http://127.0.0.1:8000/v1/amazon/inventory/{product_id}/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"quantity": 100}'
```

---

# FACEBOOK CLONE

Base: `/v1/facebook`

## Public Endpoints

### Posts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/posts/{id}/` | Get post |
| GET | `/posts/trending/` | Trending posts |
| GET | `/search/posts/` | Search posts |

```bash
curl http://127.0.0.1:8000/v1/facebook/posts/trending/
curl "http://127.0.0.1:8000/v1/facebook/search/posts/?q=hello"
```

## Private Endpoints (Require Auth)

### Posts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/posts/` | List my posts |
| POST | `/posts/` | Create post |
| GET | `/posts/feed/` | Get feed |
| PATCH | `/posts/{id}/` | Update post |
| DELETE | `/posts/{id}/` | Delete post |

```bash
# Create post
curl -X POST http://127.0.0.1:8000/v1/facebook/posts/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"body": "Hello world!", "privacy": "public"}'

# Get feed
curl http://127.0.0.1:8000/v1/facebook/posts/feed/ \
  -H "Authorization: Bearer <token>"
```

### Comments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/posts/{id}/comments/` | List comments |
| POST | `/posts/{id}/comments/` | Add comment |
| PATCH | `/comments/{id}/` | Update comment |
| DELETE | `/comments/{id}/` | Delete comment |

```bash
# Add comment
curl -X POST http://127.0.0.1:8000/v1/facebook/posts/{post_id}/comments/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"body": "Great post!"}'
```

### Reactions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/posts/{id}/reactions/` | React to post |
| DELETE | `/posts/{id}/reactions/` | Remove reaction |

```bash
# React to post
curl -X POST http://127.0.0.1:8000/v1/facebook/posts/{post_id}/reactions/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"type": "like"}'
```

### Friendships
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/friends/requests/` | Send friend request |
| GET | `/friends/requests/` | List requests |
| POST | `/friends/requests/{id}/accept/` | Accept |
| POST | `/friends/requests/{id}/decline/` | Decline |
| GET | `/users/{id}/friends/` | Get user's friends |
| DELETE | `/friends/{userId}/` | Unfriend |

```bash
# Send friend request
curl -X POST http://127.0.0.1:8000/v1/facebook/friends/requests/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"toUserId": "<user_uuid>"}'

# Accept request
curl -X POST http://127.0.0.1:8000/v1/facebook/friends/requests/{request_id}/accept/ \
  -H "Authorization: Bearer <token>"
```

### Groups
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/groups/` | List groups |
| POST | `/groups/` | Create group |
| GET | `/groups/{slug}/` | Get group |
| POST | `/groups/{slug}/join/` | Join group |
| POST | `/groups/{slug}/leave/` | Leave group |

```bash
# Create group
curl -X POST http://127.0.0.1:8000/v1/facebook/groups/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Group", "slug": "my-group", "privacy": "public"}'
```

### Pages
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/pages/` | List pages |
| POST | `/pages/` | Create page |
| POST | `/pages/{slug}/follow/` | Follow page |
| DELETE | `/pages/{slug}/follow/` | Unfollow |

### Messaging
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/threads/` | List threads |
| POST | `/threads/` | Create thread |
| GET | `/threads/{id}/messages/` | Get messages |
| POST | `/threads/{id}/messages/` | Send message |

```bash
# Create thread
curl -X POST http://127.0.0.1:8000/v1/facebook/threads/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"participantIds": ["<user_uuid>"]}'

# Send message
curl -X POST http://127.0.0.1:8000/v1/facebook/threads/{thread_id}/messages/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"body": "Hello!"}'
```

---

# INSTAGRAM CLONE

Base: `/v1/instagram`

## Public Endpoints

### Media
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/media/{id}/` | Get media |
| GET | `/media/{id}/likes/` | Get likes |
| GET | `/media/{id}/comments/` | Get comments |
| GET | `/explore/` | Explore feed |
| GET | `/tags/` | Search tags |

```bash
curl http://127.0.0.1:8000/v1/instagram/explore/
curl http://127.0.0.1:8000/v1/instagram/media/{media_id}/
```

## Private Endpoints (Require Auth)

### Media
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/feed/` | My feed |
| POST | `/media/` | Upload media |
| PATCH | `/media/{id}/` | Update caption |
| DELETE | `/media/{id}/` | Delete |
| POST | `/media/{id}/like/` | Like |
| DELETE | `/media/{id}/like/` | Unlike |

```bash
# Upload media
curl -X POST http://127.0.0.1:8000/v1/instagram/media/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "image",
    "urls": {"items": [{"url": "https://picsum.photos/800/800", "width": 800, "height": 800}]},
    "caption": "My photo #cool"
  }'

# Like
curl -X POST http://127.0.0.1:8000/v1/instagram/media/{media_id}/like/ \
  -H "Authorization: Bearer <token>"
```

### Follow
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/users/{id}/follow/` | Follow |
| DELETE | `/users/{id}/follow/` | Unfollow |
| GET | `/users/{id}/followers/` | Get followers |
| GET | `/users/{id}/following/` | Get following |

```bash
# Follow user
curl -X POST http://127.0.0.1:8000/v1/instagram/users/{user_id}/follow/ \
  -H "Authorization: Bearer <token>"
```

### Stories
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/stories/` | Following stories |
| POST | `/stories/` | Create story |
| POST | `/stories/{id}/view/` | View story |
| DELETE | `/stories/{id}/` | Delete |

### Direct Messages
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dm/threads/` | List threads |
| POST | `/dm/threads/` | Create thread |
| GET | `/dm/threads/{id}/messages/` | Get messages |
| POST | `/dm/threads/{id}/messages/send/` | Send |

```bash
# Create thread
curl -X POST http://127.0.0.1:8000/v1/instagram/dm/threads/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"participantIds": ["<user_uuid>"]}'
```

---

## Error Response Format

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description",
    "details": []
  }
}
```

---

## Pagination Format

All list endpoints return:
```json
{
  "data": [...],
  "page": 1,
  "limit": 20,
  "total": 100
}
```

Query params: `?page=1&limit=50`
