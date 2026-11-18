| family | cases | gpt-oss-120b | gpt-oss-20b | north-mini-code | qwen3.8-27b | dots-3-note | all five models |
|---|---|---|---|---|---|---|---|
| F1 period | C01 C04 C05 C06 C07 C20 | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 | 30/30 |
| F3 product list | C03 C12 C13 C14 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 20/20 |
| F2 age on a reference date | C02 C08 C09 C11 | 4/4 | 1/4 (wrong C02,C08,C11) | 0/4 (wrong C02,C08,C09,C11) | 4/4 | 2/4 (wrong C02,C08) | 11/20 |
| F2b age at the order | C10 | 1/1 | 1/1 | 0/1 (wrong C10) | 0/1 (wrong C10) | 0/1 (wrong C10) | 2/5 |
| F1+F2 | C15 | 1/1 | 1/1 | 1/1 | 0/1 (wrong C15) | 0/1 (wrong C15) | 3/5 |
| F2+F3 | C16 | 1/1 | 1/1 | 1/1 | 1/1 | 0/1 (wrong C16) | 4/5 |
| F1+F2+F3 | C17 C19 | 2/2 | 2/2 | 1/2 (wrong C17) | 0/2 (wrong C19; not run (HTTP 429) C17) | 1/2 (wrong C17) | 6/10 |
| F1+F2b | C18 | 1/1 | 1/1 | 1/1 | 1/1 | 0/1 (wrong C18) | 4/5 |
| any F2 (F2 alone or combined) | C02 C08 C09 C11 C15 C16 C17 C19 | 8/8 | 5/8 (wrong C02,C08,C11) | 3/8 (wrong C02,C08,C09,C11,C17) | 5/8 (wrong C15,C19; not run (HTTP 429) C17) | 3/8 (wrong C02,C08,C15,C16,C17) | 24/40 |
| any F2b (F2b alone or combined) | C10 C18 | 2/2 | 2/2 | 1/2 (wrong C10) | 1/2 (wrong C10) | 0/2 (wrong C10,C18) | 6/10 |
| F1 or F3 without age (C01, C03-C07, C12-C14, C20) | C01 C03 C04 C05 C06 C07 C12 C13 C14 C20 | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 | 50/50 |
