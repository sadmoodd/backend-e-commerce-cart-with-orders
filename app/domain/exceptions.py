class DomainError(ValueError):
    pass


class CannotAddProductWithoutStock(DomainError):
    pass


class ProductNotInCartError(DomainError):
    pass