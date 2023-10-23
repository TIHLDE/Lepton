use reqwest::{header, ClientBuilder};
use reqwest::{Client, Result};
use serde::{Deserialize, Serialize};
use std::time::Duration;

const API_URL: &str = "http://localhost:8000";
fn api(str: &str) -> String {
    format!("{}{}", API_URL, str)
}

#[tokio::main]
async fn main() -> Result<()> {
    let timeout = Duration::new(20, 0);

    let client = ClientBuilder::new().timeout(timeout).build()?;

    let admin_token = get_token(&client, &User::new("index", "index123")).await?;

    Ok(())
}

#[derive(Debug, Serialize, Deserialize)]
struct User {
    user_id: String,
    password: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct Token {
    token: String,
}

struct UserClient {
    token: Token,
    user: User,
}

impl User {
    fn new(username: &str, password: &str) -> Self {
        Self {
            user_id: username.to_string(),
            password: password.to_string(),
        }
    }
}

async fn create_user(client: &Client, admin_token: Token, user: &User) -> Result<()> {
    let res = client.post(api("/users"));
    Ok(())
}

async fn get_token(client: &Client, user: &User) -> Result<Token> {
    let res = client
        .post(api("/auth/login"))
        .headers(get_headers())
        .body(serde_json::to_string(user).unwrap())
        .send()
        .await?
        .text()
        .await?;

    dbg!(&res);

    let token = serde_json::from_str::<Token>(&res).unwrap();

    Ok(token)
}

fn get_headers() -> header::HeaderMap {
    let mut headers = header::HeaderMap::new();
    headers.insert(
        header::CONTENT_TYPE,
        header::HeaderValue::from_static("application/json"),
    );
    headers.insert(header::CONNECTION, "keep-alive".parse().unwrap());

    headers
}
