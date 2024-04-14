# FlashCard
FlashCard website

DB schema

1. `col` (Collection options):
    - `id`: Collection ID
    - `crt`: Collection creation time
    - `mod`: Last modification time
    - `scm`: Schema modification time
    - `ver`: Version
    - `dty`: Dirty flag
    - `usn`: Update sequence number
    - `ls`: Last sync time
    - `conf`: Configuration options
    - `models`: Deck models
    - `decks`: Decks
    - `dconf`: Deck configuration
    - `tags`: Tags

2. `notes` (Notes, which can generate one or more cards):
    - `id`: Note ID
    - `guid`: Globally unique ID
    - `mid`: Model ID
    - `mod`: Last modification time
    - `usn`: Update sequence number
    - `tags`: Space-separated list of tags
    - `flds`: The values of the note's fields, separated by 0x1f (31) character
    - `sfld`: Sort field
    - `csum`: Checksum of the first field
    - `flags`: Currently unused
    - `data`: Currently unused

3. `cards` (Cards, which are generated from notes):
    - `id`: Card ID
    - `nid`: Note ID
    - `did`: Deck ID
    - `ord`: Ordinal (the card's place in the note)
    - `mod`: Last modification time
    - `usn`: Update sequence number
    - `type`: Card type
    - `queue`: Queue state
    - `due`: Due date
    - `ivl`: Interval
    - `factor`: Ease factor
    - `reps`: Number of reviews
    - `lapses`: Number of lapses
    - `left`: Reviews left till graduation
    - `odue`: Original due date (for cards in filtered deck)
    - `odid`: Original deck ID (for cards in filtered deck)
    - `flags`: Currently unused
    - `data`: Currently unused

4. `revlog` (Review logs):
    - `id`: Review ID
    - `cid`: Card ID
    - `usn`: Update sequence number
    - `ease`: Ease factor
    - `ivl`: Interval
    - `lastIvl`: Last interval
    - `factor`: Ease factor
    - `time`: Review time
    - `type`: Review type

5. `graves` (Deleted items):
    - `usn`: Update sequence number
    - `oid`: Original ID
    - `type`: Type of the deleted item

6. `sqlite_stat1` (Internal SQLite statistics table):
    - `tbl`: Table name
    - `idx`: Index name
    - `stat`: Statistical data

Please note that the exact structure can vary depending on the version of Anki you are using. If you have a specific question about a table or field, feel free to ask!
