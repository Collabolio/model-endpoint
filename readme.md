# User Similarity API

This API allows you to find the top N most similar users to a given user based on their skills and interests.

## API ENDPOINT

`https://model-endpoint-onhqnm5xvq-uc.a.run.app`

## Usage

Send a `GET` request to `/api/users/<string:uid>/<int:n>` to retrieve the top N most similar users to the user with ID `uid`.

### Request

- `uid` : string, required. The user ID of the user for whom you want to find similar users.
- `n` : string, required. The number of most similar users to return.

### Response

The response is a list of dictionaries, where each dictionary contains the user ID (`uid`) and their similarity score (`similarity_score`). The similarity score is a value between 0 and 1, where 1 indicates a perfect match.

### Example

```bash
$ curl https://model-endpoint-onhqnm5xvq-uc.a.run.app/api/users/06yJpLuZ79Dbzyky0TQL/10

[
    {
        "similarity_score": 0.8476112484931946,
        "uid": "DlmikRZzUud87ZVHWPBv"
    },
    {
        "similarity_score": 0.7643425464630127,
        "uid": "GYWVAv9MsocnhgVqZHfn"
    },
    {
        "similarity_score": 0.7564221024513245,
        "uid": "yNY9IhalltJZ02tQU0ix"
    },
    {
        "similarity_score": 0.755081057548523,
        "uid": "J5GkwKqxI217nMLNdY1B"
    },
    {
        "similarity_score": 0.7529898285865784,
        "uid": "OtatlU0hDcex4Cn5dRKN"
    },
    {
        "similarity_score": 0.7501305937767029,
        "uid": "vbxf5J04EfvCznIapW3H"
    },
    {
        "similarity_score": 0.7341395616531372,
        "uid": "AvufTNycNTN9p5aicfjv"
    },
    {
        "similarity_score": 0.734026312828064,
        "uid": "6mDvGWpmuiCzNoWqkLfP"
    },
    {
        "similarity_score": 0.7308772802352905,
        "uid": "Gt6OGPcCTzzz2waskmn2"
    }
]
```
