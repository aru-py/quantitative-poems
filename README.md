# Quantitative Poems

## Overview

Quantitative Poems is a book about what makes us human, written by a machine. It’s a collection of mathematical poems that try to capture the landscape of consciousness – the ineffable experiences, such as joy, love, and wonder. It’s an absurdist response to the questioning of our identity and our place in the universe.

## Generating the book

If you're interested (and have lots of spare Anthropic credits), you can generate the book yourself.

### Prerequisites

Ensure you have the following tools installed:

-   **Pipenv**: A tool for managing Python packages. [Install from here](https://pipenv.pypa.io/en/latest/).
-   **Lualatex**: A typesetting system. [Learn more](https://www.luatex.org/).

### Usage

1.  **Clone repository**: Clone the project's repository to your local machine. Replace <repo-url> with the actual URL of the repository.
```
git pull <repo-url>
```
2.  **Install dependencies**: Navigate to the project directory and install the necessary dependencies using Pipenv.
```
cd quantitative-poems
pipenv install
```
3.  **Generate Book**: Run the `main book build` command to generate book.
```
pipenv run main book build
```

## Contributions

Contributions are welcome! If you're interested, please [open an issue](https://github.com/aru-py/quantitative-poems/issues/new) with your proposed changes!
