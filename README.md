

## Canidate implementations for a standardized directory hash in python packaging.

### _blake_based.py:hash_dir

- Uses blake2's tree based construction and personalization strings
- Does not need to restrict filenames.
- Captures the name of the directory.
- Captures empty directories since these change the behavior of import in python.
- recursive and extremely parallelizable.
    - only need to hold node hashes until a parent node in the tree is calculated.
    - do not need to hold filenames.

### _sha256_based.py:hash_dir

- Disallows newlines in filenames.
- Does not capture the name of the directory.
- Captures empty directories since these change the behavior of import in python.
- recursive and highly parallelizable.
    - Need to hold node hashes and filenames until parent node is calculated.

### _go_dirhash_deriv.py:hash_dir

- Disallows newlines in filenames.
- Does not capture the name of the directory.
- cannot capture empty directories without deviating from go's design.
- relies on Path.as_posix() for portable path representation.
- iterative and somewhat parallelizable
    - requires sorting the full recursively walked filelist.
    - requires holding all filenames and hashes until the end.


### Things all 3 have in common

- Believed to be safe construction with adequate domain seperation.
- Versionable and identifiable.
- Disallows symlinks outside of the directory.
    (*lockers* can hash and lock multiple direcotries on behalf of users where this is desirable)


## Sample use and output

example.py hashes the directory_hash directory

-B is to avoid writing bytecode into the directory

```
python -B example.py
Ran go (h1) in 0.000691999914124608
h1:9929b5e0ad3b41203c0ff2c6bc8abfbbfa350b57b7c5f8cf5aa9e8435cabcdac
Ran sha256_based (s1) in 0.0006723999977111816
s1:44a3028ed24482f664d2120516f0c279e1600360b43fe361eb426947bb3b99d6
Ran blake2 based (b1) in 0.0005755999591201544
b1:993e815939da5b95f72bdeb222dcdf0bd469c1acb333bf8bc4017234143e374f
```

## Remaining tasks

- Attempt to reach consensus on one or more of these approaches
- Fully document the surviving functions in a language independent manner
- Propose a standards pep using the surviving functions