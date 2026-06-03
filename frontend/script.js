const API_URL = "http://127.0.0.1:8000";

let token = "";


async function registerUser() {

    const body = {
        full_name: document.getElementById("regName").value,
        email: document.getElementById("regEmail").value,
        password: document.getElementById("regPassword").value,
        role: document.getElementById("regRole").value
    };

    const res = await fetch(
        `${API_URL}/auth/register`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(body)
        }
    );

    alert("User Registered");
}


async function loginUser() {

    const body = {
        email: document.getElementById("loginEmail").value,
        password: document.getElementById("loginPassword").value
    };

    const res = await fetch(
        `${API_URL}/auth/login`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(body)
        }
    );

    const data = await res.json();

    token = data.access_token;

    alert("Login Successful");
}


async function createProduct() {

    const body = {

        sku: document.getElementById("sku").value,

        name: document.getElementById("productName").value,

        description: "",

        category: "",

        tags: "",

        price: parseFloat(
            document.getElementById("price").value
        ),

        stock: parseInt(
            document.getElementById("stock").value
        )
    };

    await fetch(
        `${API_URL}/products/`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },

            body: JSON.stringify(body)
        }
    );

    alert("Product Created");
}


async function loadProducts() {

    const res = await fetch(
        `${API_URL}/products/`
    );

    const products = await res.json();

    let html = "";

    products.forEach(p => {

        html += `
        <div class="product">
            <b>${p.name}</b><br>
            Price: ${p.price}<br>
            Stock: ${p.stock}
        </div>
        `;
    });

    document.getElementById(
        "products"
    ).innerHTML = html;
}


async function createOrder() {

    const body = {

        items: [
            {
                product_id: parseInt(
                    document.getElementById(
                        "orderProductId"
                    ).value
                ),

                quantity: parseInt(
                    document.getElementById(
                        "orderQuantity"
                    ).value
                )
            }
        ]
    };

    const res = await fetch(
        `${API_URL}/orders/`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },

            body: JSON.stringify(body)
        }
    );

    const data = await res.json();

    alert(
        "Order Created: " +
        data.order_number
    );
}


async function loadOrders() {

    const res = await fetch(
        `${API_URL}/orders/`,
        {
            headers: {
                "Authorization":
                `Bearer ${token}`
            }
        }
    );

    const orders = await res.json();

    let html = "";

    orders.forEach(o => {

        html += `
        <div class="order">
            <b>${o.order_number}</b><br>
            Status: ${o.status}<br>
            Total: ${o.total_amount}
        </div>
        `;
    });

    document.getElementById(
        "orders"
    ).innerHTML = html;
}


async function generateMetadata() {

    const body = {

        product_name:
        document.getElementById(
            "metaProduct"
        ).value
    };

    const res = await fetch(
        `${API_URL}/products/suggest-metadata`,
        {
            method: "POST",

            headers: {
                "Content-Type":
                "application/json"
            },

            body: JSON.stringify(body)
        }
    );

    const data = await res.json();

    document.getElementById(
        "metadataResult"
    ).innerText =
        JSON.stringify(
            data,
            null,
            2
        );
}