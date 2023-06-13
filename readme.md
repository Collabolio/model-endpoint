# User Similarity API

This API allows you to find the top N most similar users to a given user based on their skills and interests.

## Usage

Send a `GET` request to `/api/users/<string:uid>/<string:n>` to retrieve the top N most similar users to the user with ID `uid`.

### Request

- `uid` : string, required. The user ID of the user for whom you want to find similar users.
- `n` : string, required. The number of most similar users to return.

### Response

The response is a list of dictionaries, where each dictionary contains the user ID (`uid`) and their similarity score (`similarity_score`). The similarity score is a value between 0 and 1, where 1 indicates a perfect match.

### Example

```bash
$ curl https://model-endpoint-onhqnm5xvq-uc.a.run.app/api/users/12345/5

[
    {
        "uid": "67890",
        "similarity_score": 0.9562
    },
    {
        "uid": "54321",
        "similarity_score": 0.9456
    },
    {
        "uid": "98765",
        "similarity_score": 0.9345
    },
    {
        "uid": "23456",
        "similarity_score": 0.9123
    },
    {
        "uid": "34567",
        "similarity_score": 0.9023
    }
]
```
