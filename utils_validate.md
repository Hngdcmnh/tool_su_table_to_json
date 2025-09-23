# Các cái hợp lệ

```bash
Question
Intent_Response (...)
Intent_Response (...)
Intent_Response (fallback)
Intent_Response (silence)
```
=> Cái này oke nha. 


---

## Các cái ko hợp lệ 

```bash 
Question
Intent_Response (...)
Intent_Response (fallback)
```

```bash
Question
Intent_Response (silence)
```
```bash
Question
Intent_Response (...)
Intent_Response (...)
```

---


**Các trường hợp hợp lệ:**
- Question → ... → ... → fallback → silence ✓
- Question → fallback → ... → silence ✓
- Question → silence → fallback ✓
- Question → ... → silence → ... → fallback ✓

**Các trường hợp không hợp lệ:**
- Question → ... → fallback (thiếu silence) ✗
- Question → silence (thiếu fallback) ✗
- Question → ... → ... (thiếu cả fallback và silence) ✗