# Backend REST API Documentation

All endpoints receive and return JSON data.

## /search (GET)

Search for a number of tracks using keywords in the title.

### Request

```
{
    query: string (255 char max)
}
```

### Response

```
[
    {
        name: string
        artistName: string
        audioUrl: string
        imageUrl: string
        duration: int (in seconds)
    }
]
```
