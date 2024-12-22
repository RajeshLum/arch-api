from django.db import models


class SanctionedEntity(models.Model):
    sanctionId = models.CharField(max_length=255, unique=True)
    caption = models.CharField(max_length=255)
    schema = models.CharField(max_length=50)
    referents = models.JSONField(blank=True, null=True)
    datasets = models.JSONField(blank=True, null=True)
    first_seen = models.DateTimeField(blank=True, null=True)
    last_seen = models.DateTimeField(blank=True, null=True)
    last_change = models.DateTimeField(blank=True, null=True)
    target = models.BooleanField(default=False)

    def __str__(self):
        return self.caption

    class Meta:
        verbose_name_plural = "SanctionedEntities"


class Person(models.Model):
    sanctionEntity = models.OneToOneField(
        SanctionedEntity,
        on_delete=models.CASCADE,
    )

    name = models.JSONField(blank=True, null=True)
    summary = models.JSONField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    country = models.JSONField(blank=True, null=True)
    alias = models.JSONField(blank=True, null=True)
    previousName = models.JSONField(blank=True, null=True)
    weakAlias = models.JSONField(blank=True, null=True)
    sourceUrl = models.JSONField(blank=True, null=True)
    publisher = models.JSONField(blank=True, null=True)
    wikidataId = models.JSONField(blank=True, null=True)
    keywords = models.JSONField(blank=True, null=True)
    topics = models.JSONField(blank=True, null=True)
    address = models.JSONField(blank=True, null=True)
    addressEntity = models.JSONField(blank=True, null=True)
    program = models.JSONField(blank=True, null=True)
    notes = models.JSONField(blank=True, null=True)
    createdAt = models.JSONField(blank=True, null=True)
    modifiedAt = models.JSONField(blank=True, null=True)

    email = models.JSONField(blank=True, null=True)
    phone = models.JSONField(blank=True, null=True)
    website = models.JSONField(blank=True, null=True)
    legalForm = models.JSONField(blank=True, null=True)
    incorporationDate = models.JSONField(blank=True, null=True)
    dissolutionDate = models.JSONField(blank=True, null=True)
    status = models.JSONField(blank=True, null=True)
    sector = models.JSONField(blank=True, null=True)
    classification = models.JSONField(blank=True, null=True)
    registrationNumber = models.JSONField(blank=True, null=True)
    idNumber = models.JSONField(blank=True, null=True)
    taxNumber = models.JSONField(blank=True, null=True)
    vatCode = models.JSONField(blank=True, null=True)
    jurisdiction = models.JSONField(blank=True, null=True)
    mainCountry = models.JSONField(blank=True, null=True)
    opencorporatesUrl = models.JSONField(blank=True, null=True)
    icijId = models.JSONField(blank=True, null=True)
    okpoCode = models.JSONField(blank=True, null=True)
    innCode = models.JSONField(blank=True, null=True)
    ogrnCode = models.JSONField(blank=True, null=True)
    leiCode = models.JSONField(blank=True, null=True)
    dunsCode = models.JSONField(blank=True, null=True)
    uniqueEntityId = models.JSONField(blank=True, null=True)
    npiCode = models.JSONField(blank=True, null=True)
    swiftBic = models.JSONField(blank=True, null=True)
    parent = models.JSONField(blank=True, null=True)

    title = models.JSONField(blank=True, null=True)
    firstName = models.JSONField(blank=True, null=True)
    secondName = models.JSONField(blank=True, null=True)
    middleName = models.JSONField(blank=True, null=True)
    fatherName = models.JSONField(blank=True, null=True)
    motherName = models.JSONField(blank=True, null=True)
    lastName = models.JSONField(blank=True, null=True)
    nameSuffix = models.JSONField(blank=True, null=True)
    birthDate = models.JSONField(blank=True, null=True)
    birthPlace = models.JSONField(blank=True, null=True)
    birthCountry = models.JSONField(blank=True, null=True)
    deathDate = models.JSONField(blank=True, null=True)
    position = models.JSONField(blank=True, null=True)
    nationality = models.JSONField(blank=True, null=True)
    citizenship = models.JSONField(blank=True, null=True)
    passportNumber = models.JSONField(blank=True, null=True)
    socialSecurityNumber = models.JSONField(blank=True, null=True)
    gender = models.JSONField(blank=True, null=True)
    ethnicity = models.JSONField(blank=True, null=True)
    height = models.JSONField(blank=True, null=True)
    weight = models.JSONField(blank=True, null=True)
    eyeColor = models.JSONField(blank=True, null=True)
    hairColor = models.JSONField(blank=True, null=True)
    appearance = models.JSONField(blank=True, null=True)
    religion = models.JSONField(blank=True, null=True)
    political = models.JSONField(blank=True, null=True)
    education = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.name[0]}".strip()

    class Meta:
        verbose_name_plural = "People"


class Sanction(models.Model):
    sanctionEntity = models.OneToOneField(
        SanctionedEntity,
        on_delete=models.CASCADE,
    )
    entity = models.JSONField(blank=True, null=True)
    startDate = models.JSONField(blank=True, null=True)
    endDate = models.JSONField(blank=True, null=True)
    date = models.JSONField(blank=True, null=True)
    summary = models.JSONField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    recordId = models.CharField(max_length=1024, blank=True, null=True)
    sourceUrl = models.JSONField(blank=True, null=True)
    publisher = models.JSONField(blank=True, null=True)
    modifiedAt = models.JSONField(blank=True, null=True)

    authority = models.JSONField(blank=True, null=True)
    authorityId = models.JSONField(blank=True, null=True)
    unscId = models.JSONField(blank=True, null=True)
    program = models.JSONField(blank=True, null=True)
    programId = models.JSONField(blank=True, null=True)
    programUrl = models.JSONField(blank=True, null=True)
    provisions = models.JSONField(blank=True, null=True)
    status = models.JSONField(blank=True, null=True)
    duration = models.JSONField(blank=True, null=True)
    reason = models.JSONField(blank=True, null=True)
    country = models.JSONField(blank=True, null=True)
    listingDate = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Sanction for {self.entity}"

    class Meta:
        verbose_name_plural = "Sanctions"


class Family(models.Model):
    sanctionEntity = models.OneToOneField(
        SanctionedEntity, on_delete=models.CASCADE, unique=True
    )

    startDate = models.JSONField(blank=True, null=True)
    endDate = models.JSONField(blank=True, null=True)
    date = models.JSONField(blank=True, null=True)
    summary = models.JSONField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    recordId = models.JSONField(blank=True, null=True)
    sourceUrl = models.JSONField(blank=True, null=True)
    publisher = models.JSONField(blank=True, null=True)
    modifiedAt = models.JSONField(blank=True, null=True)

    person = models.JSONField(blank=True, null=True)
    relative = models.JSONField(blank=True, null=True)
    relationship = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Family relationship between {self.person} and {self.relative}"

    class Meta:
        verbose_name_plural = "Families"


class CryptoWallet(models.Model):
    sanctionEntity = models.OneToOneField(
        SanctionedEntity,
        on_delete=models.CASCADE,
    )

    name = models.JSONField(blank=True, null=True)
    summary = models.JSONField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    country = models.JSONField(blank=True, null=True)
    alias = models.JSONField(blank=True, null=True)
    previousName = models.JSONField(blank=True, null=True)
    weakAlias = models.JSONField(blank=True, null=True)
    sourceUrl = models.JSONField(blank=True, null=True)
    publisher = models.JSONField(blank=True, null=True)
    wikidataId = models.JSONField(blank=True, null=True)
    keywords = models.JSONField(blank=True, null=True)
    topics = models.JSONField(blank=True, null=True)
    address = models.JSONField(blank=True, null=True)
    addressEntity = models.JSONField(blank=True, null=True)
    program = models.JSONField(blank=True, null=True)
    notes = models.JSONField(blank=True, null=True)
    createdAt = models.JSONField(blank=True, null=True)
    modifiedAt = models.JSONField(blank=True, null=True)

    amount = models.JSONField(blank=True, null=True)
    currency = models.JSONField(blank=True, null=True)
    amountUsd = models.JSONField(blank=True, null=True)

    publicKey = models.JSONField(blank=True, null=True)
    mangingExchange = models.JSONField(blank=True, null=True)
    holder = models.JSONField(blank=True, null=True)
    balance = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Crypto Wallet for {self.name}"

    class Meta:
        verbose_name_plural = "CryptoWallets"


class Succession(models.Model):
    sanctionEntity = models.OneToOneField(
        SanctionedEntity,
        on_delete=models.CASCADE,
    )

    startDate = models.JSONField(blank=True, null=True)
    endDate = models.JSONField(blank=True, null=True)
    date = models.JSONField(blank=True, null=True)
    summary = models.JSONField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    recordId = models.JSONField(blank=True, null=True)
    sourceUrl = models.JSONField(blank=True, null=True)
    publisher = models.JSONField(blank=True, null=True)
    modifiedAt = models.JSONField(blank=True, null=True)

    role = models.JSONField(blank=True, null=True)
    status = models.JSONField(blank=True, null=True)

    predecessor = models.JSONField(blank=True, null=True)
    successor = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Succession between {self.predecessor} and {self.successor}"

    class Meta:
        verbose_name_plural = "Successions"


class Company(models.Model):
    sanctionEntity = models.OneToOneField(
        SanctionedEntity,
        on_delete=models.CASCADE,
    )

    name = models.JSONField(blank=True, null=True)
    summary = models.JSONField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    country = models.JSONField(blank=True, null=True)
    alias = models.JSONField(blank=True, null=True)
    previousName = models.JSONField(blank=True, null=True)
    weakAlias = models.JSONField(blank=True, null=True)
    sourceUrl = models.JSONField(blank=True, null=True)
    publisher = models.JSONField(blank=True, null=True)
    wikidataId = models.JSONField(blank=True, null=True)
    keywords = models.JSONField(blank=True, null=True)
    topics = models.JSONField(blank=True, null=True)
    address = models.JSONField(blank=True, null=True)
    addressEntity = models.JSONField(blank=True, null=True)
    program = models.JSONField(blank=True, null=True)
    notes = models.JSONField(blank=True, null=True)
    createdAt = models.JSONField(blank=True, null=True)
    modifiedAt = models.JSONField(blank=True, null=True)

    amount = models.JSONField(blank=True, null=True)
    currency = models.JSONField(blank=True, null=True)
    amountUsd = models.JSONField(blank=True, null=True)

    email = models.JSONField(blank=True, null=True)
    phone = models.JSONField(blank=True, null=True)
    website = models.JSONField(blank=True, null=True)
    legalForm = models.JSONField(blank=True, null=True)
    incorporationDate = models.JSONField(blank=True, null=True)
    dissolutionDate = models.JSONField(blank=True, null=True)
    status = models.JSONField(blank=True, null=True)
    sector = models.JSONField(blank=True, null=True)
    classification = models.JSONField(blank=True, null=True)

    registrationNumber = models.JSONField(blank=True, null=True)
    idNumber = models.JSONField(blank=True, null=True)
    taxNumber = models.JSONField(blank=True, null=True)
    vatCode = models.JSONField(blank=True, null=True)

    jurisdiction = models.JSONField(blank=True, null=True)
    mainCountry = models.JSONField(blank=True, null=True)
    opencorporatesUrl = models.JSONField(blank=True, null=True)
    icijId = models.JSONField(blank=True, null=True)
    okpoCode = models.JSONField(blank=True, null=True)
    innCode = models.JSONField(blank=True, null=True)
    ogrnCode = models.JSONField(blank=True, null=True)
    leiCode = models.JSONField(blank=True, null=True)
    dunsCode = models.JSONField(blank=True, null=True)
    uniqueEntityId = models.JSONField(blank=True, null=True)
    npiCode = models.JSONField(blank=True, null=True)
    swiftBic = models.JSONField(blank=True, null=True)
    parent = models.JSONField(blank=True, null=True)

    cageCode = models.JSONField(blank=True, null=True)
    permId = models.JSONField(blank=True, null=True)
    imoNumber = models.JSONField(blank=True, null=True)
    giiNumber = models.JSONField(blank=True, null=True)

    cikCode = models.JSONField(blank=True, null=True)
    kppCode = models.JSONField(blank=True, null=True)
    bikCode = models.JSONField(blank=True, null=True)
    ticker = models.JSONField(blank=True, null=True)
    ricCode = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Company: {self.name}"

    class Meta:
        verbose_name_plural = "Companies"


class Ownership(models.Model):
    sanctionEntity = models.OneToOneField(
        SanctionedEntity,
        on_delete=models.CASCADE,
    )

    startDate = models.JSONField(blank=True, null=True)
    endDate = models.JSONField(blank=True, null=True)
    date = models.JSONField(blank=True, null=True)
    summary = models.JSONField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    recordId = models.JSONField(blank=True, null=True)
    sourceUrl = models.JSONField(blank=True, null=True)
    publisher = models.JSONField(blank=True, null=True)
    modifiedAt = models.JSONField(blank=True, null=True)

    role = models.JSONField(blank=True, null=True)
    status = models.JSONField(blank=True, null=True)

    owner = models.JSONField(blank=True, null=True)
    asset = models.JSONField(blank=True, null=True)
    percentage = models.JSONField(blank=True, null=True)
    sharesCount = models.JSONField(blank=True, null=True)
    sharesValue = models.JSONField(blank=True, null=True)
    sharesCurrency = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Ownership of {self.asset} by {self.owner}"

    class Meta:
        verbose_name_plural = "Ownerships"


class Vessel(models.Model):
    sanctionEntity = models.OneToOneField(
        SanctionedEntity,
        on_delete=models.CASCADE,
    )

    name = models.JSONField(blank=True, null=True)
    summary = models.JSONField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    country = models.JSONField(blank=True, null=True)
    alias = models.JSONField(blank=True, null=True)
    previousName = models.JSONField(blank=True, null=True)
    weakAlias = models.JSONField(blank=True, null=True)
    sourceUrl = models.JSONField(blank=True, null=True)
    publisher = models.JSONField(blank=True, null=True)
    wikidataId = models.JSONField(blank=True, null=True)
    keywords = models.JSONField(blank=True, null=True)
    topics = models.JSONField(blank=True, null=True)
    address = models.JSONField(blank=True, null=True)
    addressEntity = models.JSONField(blank=True, null=True)
    program = models.JSONField(blank=True, null=True)
    notes = models.JSONField(blank=True, null=True)
    createdAt = models.JSONField(blank=True, null=True)
    modifiedAt = models.JSONField(blank=True, null=True)

    amount = models.JSONField(blank=True, null=True)
    currency = models.JSONField(blank=True, null=True)
    amountUsd = models.JSONField(blank=True, null=True)

    registrationNumber = models.JSONField(blank=True, null=True)
    type = models.JSONField(blank=True, null=True)
    model = models.JSONField(blank=True, null=True)
    owner = models.JSONField(blank=True, null=True)
    buildDate = models.JSONField(blank=True, null=True)

    imoNumber = models.JSONField(blank=True, null=True)
    flag = models.JSONField(blank=True, null=True)
    tonnage = models.JSONField(blank=True, null=True)
    grossRegisteredTonnage = models.JSONField(blank=True, null=True)
    callSign = models.JSONField(blank=True, null=True)
    pastFlags = models.JSONField(blank=True, null=True)
    mmsi = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Vessel {self.name}"

    class Meta:
        verbose_name_plural = "Vessels"


class Position(models.Model):
    sanctionEntity = models.OneToOneField(
        SanctionedEntity,
        on_delete=models.CASCADE,
    )

    name = models.JSONField(blank=True, null=True)
    summary = models.JSONField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    country = models.JSONField(blank=True, null=True)
    alias = models.JSONField(blank=True, null=True)
    previousName = models.JSONField(blank=True, null=True)
    weakAlias = models.JSONField(blank=True, null=True)
    sourceUrl = models.JSONField(blank=True, null=True)
    publisher = models.JSONField(blank=True, null=True)
    wikidataId = models.JSONField(blank=True, null=True)
    keywords = models.JSONField(blank=True, null=True)
    topics = models.JSONField(blank=True, null=True)
    address = models.JSONField(blank=True, null=True)
    addressEntity = models.JSONField(blank=True, null=True)
    program = models.JSONField(blank=True, null=True)
    notes = models.JSONField(blank=True, null=True)
    createdAt = models.JSONField(blank=True, null=True)
    modifiedAt = models.JSONField(blank=True, null=True)

    inceptionDate = models.JSONField(blank=True, null=True)
    dissolutionDate = models.JSONField(blank=True, null=True)
    subnationalArea = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Position {self.name}"

    class Meta:
        verbose_name_plural = "Positions"


class Asset(models.Model):
    sanctionEntity = models.OneToOneField(
        SanctionedEntity,
        on_delete=models.CASCADE,
    )

    name = models.JSONField(blank=True, null=True)
    summary = models.JSONField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    country = models.JSONField(blank=True, null=True)
    alias = models.JSONField(blank=True, null=True)
    previousName = models.JSONField(blank=True, null=True)
    weakAlias = models.JSONField(blank=True, null=True)
    sourceUrl = models.JSONField(blank=True, null=True)
    publisher = models.JSONField(blank=True, null=True)
    wikidataId = models.JSONField(blank=True, null=True)
    keywords = models.JSONField(blank=True, null=True)
    topics = models.JSONField(blank=True, null=True)
    address = models.JSONField(blank=True, null=True)
    addressEntity = models.JSONField(blank=True, null=True)
    program = models.JSONField(blank=True, null=True)
    notes = models.JSONField(blank=True, null=True)
    createdAt = models.JSONField(blank=True, null=True)
    modifiedAt = models.JSONField(blank=True, null=True)

    amount = models.JSONField(blank=True, null=True)
    currency = models.JSONField(blank=True, null=True)
    amountUsd = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Asset {self.name}"

    class Meta:
        verbose_name_plural = "Assets"


class Associate(models.Model):
    sanctionEntity = models.OneToOneField(
        SanctionedEntity,
        on_delete=models.CASCADE,
    )

    startDate = models.JSONField(blank=True, null=True)
    endDate = models.JSONField(blank=True, null=True)
    date = models.JSONField(blank=True, null=True)
    summary = models.JSONField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    recordId = models.JSONField(blank=True, null=True)
    sourceUrl = models.JSONField(blank=True, null=True)
    publisher = models.JSONField(blank=True, null=True)
    modifiedAt = models.JSONField(blank=True, null=True)

    person = models.JSONField(blank=True, null=True)
    associate = models.JSONField(blank=True, null=True)
    relationship = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Associate {self.relationship}"

    class Meta:
        verbose_name_plural = "Associates"


class Identification(models.Model):
    sanctionEntity = models.OneToOneField(
        SanctionedEntity,
        on_delete=models.CASCADE,
    )

    startDate = models.JSONField(blank=True, null=True)
    endDate = models.JSONField(blank=True, null=True)
    date = models.JSONField(blank=True, null=True)
    summary = models.JSONField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    recordId = models.JSONField(blank=True, null=True)
    sourceUrl = models.JSONField(blank=True, null=True)
    publisher = models.JSONField(blank=True, null=True)
    modifiedAt = models.JSONField(blank=True, null=True)

    holder = models.JSONField(blank=True, null=True)
    type = models.JSONField(blank=True, null=True)
    country = models.JSONField(blank=True, null=True)
    number = models.JSONField(blank=True, null=True)
    authority = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Identification {self.number}"

    class Meta:
        verbose_name_plural = "Identifications"


class Organization(models.Model):
    sanctionEntity = models.OneToOneField(
        SanctionedEntity,
        on_delete=models.CASCADE,
    )

    name = models.JSONField(blank=True, null=True)
    summary = models.JSONField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    country = models.JSONField(blank=True, null=True)
    alias = models.JSONField(blank=True, null=True)
    previousName = models.JSONField(blank=True, null=True)
    weakAlias = models.JSONField(blank=True, null=True)
    sourceUrl = models.JSONField(blank=True, null=True)
    publisher = models.JSONField(blank=True, null=True)
    wikidataId = models.JSONField(blank=True, null=True)
    keywords = models.JSONField(blank=True, null=True)
    topics = models.JSONField(blank=True, null=True)
    address = models.JSONField(blank=True, null=True)
    addressEntity = models.JSONField(blank=True, null=True)
    program = models.JSONField(blank=True, null=True)
    notes = models.JSONField(blank=True, null=True)
    createdAt = models.JSONField(blank=True, null=True)
    modifiedAt = models.JSONField(blank=True, null=True)

    email = models.JSONField(blank=True, null=True)
    phone = models.JSONField(blank=True, null=True)
    website = models.JSONField(blank=True, null=True)
    legalForm = models.JSONField(blank=True, null=True)
    incorporationDate = models.JSONField(blank=True, null=True)
    dissolutionDate = models.JSONField(blank=True, null=True)
    status = models.JSONField(blank=True, null=True)
    sector = models.JSONField(blank=True, null=True)
    classification = models.JSONField(blank=True, null=True)
    registrationNumber = models.JSONField(blank=True, null=True)
    idNumber = models.JSONField(blank=True, null=True)
    taxNumber = models.JSONField(blank=True, null=True)
    vatCode = models.JSONField(blank=True, null=True)
    jurisdiction = models.JSONField(blank=True, null=True)
    mainCountry = models.JSONField(blank=True, null=True)
    opencorporatesUrl = models.JSONField(blank=True, null=True)
    icijId = models.JSONField(blank=True, null=True)
    okpoCode = models.JSONField(blank=True, null=True)
    innCode = models.JSONField(blank=True, null=True)
    ogrnCode = models.JSONField(blank=True, null=True)
    leiCode = models.JSONField(blank=True, null=True)
    dunsCode = models.JSONField(blank=True, null=True)
    uniqueEntityId = models.JSONField(blank=True, null=True)
    npiCode = models.JSONField(blank=True, null=True)
    swiftBic = models.JSONField(blank=True, null=True)
    parent = models.JSONField(blank=True, null=True)

    cageCode = models.JSONField(blank=True, null=True)
    permId = models.JSONField(blank=True, null=True)
    imoNumber = models.JSONField(blank=True, null=True)
    giiNumber = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Organization {self.name}"

    class Meta:
        verbose_name_plural = "Organizations"


class Airplane(models.Model):
    sanctionEntity = models.OneToOneField(
        SanctionedEntity,
        on_delete=models.CASCADE,
    )

    name = models.JSONField(blank=True, null=True)
    summary = models.JSONField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    country = models.JSONField(blank=True, null=True)
    alias = models.JSONField(blank=True, null=True)
    previousName = models.JSONField(blank=True, null=True)
    weakAlias = models.JSONField(blank=True, null=True)
    sourceUrl = models.JSONField(blank=True, null=True)
    publisher = models.JSONField(blank=True, null=True)
    wikidataId = models.JSONField(blank=True, null=True)
    keywords = models.JSONField(blank=True, null=True)
    topics = models.JSONField(blank=True, null=True)
    address = models.JSONField(blank=True, null=True)
    addressEntity = models.JSONField(blank=True, null=True)
    program = models.JSONField(blank=True, null=True)
    notes = models.JSONField(blank=True, null=True)
    createdAt = models.JSONField(blank=True, null=True)
    modifiedAt = models.JSONField(blank=True, null=True)

    amount = models.JSONField(blank=True, null=True)
    currency = models.JSONField(blank=True, null=True)
    amountUsd = models.JSONField(blank=True, null=True)

    registrationNumber = models.JSONField(blank=True, null=True)
    type = models.JSONField(blank=True, null=True)
    model = models.JSONField(blank=True, null=True)
    owner = models.JSONField(blank=True, null=True)
    buildDate = models.JSONField(blank=True, null=True)
    serialNumber = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Airplane {self.name}"

    class Meta:
        verbose_name_plural = "Airplanes"


class PublicBody(models.Model):
    sanctionEntity = models.OneToOneField(
        SanctionedEntity,
        on_delete=models.CASCADE,
    )

    name = models.JSONField(blank=True, null=True)
    summary = models.JSONField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    country = models.JSONField(blank=True, null=True)
    alias = models.JSONField(blank=True, null=True)
    previousName = models.JSONField(blank=True, null=True)
    weakAlias = models.JSONField(blank=True, null=True)
    sourceUrl = models.JSONField(blank=True, null=True)
    publisher = models.JSONField(blank=True, null=True)
    wikidataId = models.JSONField(blank=True, null=True)
    keywords = models.JSONField(blank=True, null=True)
    topics = models.JSONField(blank=True, null=True)
    address = models.JSONField(blank=True, null=True)
    addressEntity = models.JSONField(blank=True, null=True)
    program = models.JSONField(blank=True, null=True)
    notes = models.JSONField(blank=True, null=True)
    createdAt = models.JSONField(blank=True, null=True)
    modifiedAt = models.JSONField(blank=True, null=True)

    email = models.JSONField(blank=True, null=True)
    phone = models.JSONField(blank=True, null=True)
    website = models.JSONField(blank=True, null=True)
    legalForm = models.JSONField(blank=True, null=True)
    incorporationDate = models.JSONField(blank=True, null=True)
    dissolutionDate = models.JSONField(blank=True, null=True)
    status = models.JSONField(blank=True, null=True)
    sector = models.JSONField(blank=True, null=True)
    classification = models.JSONField(blank=True, null=True)
    registrationNumber = models.JSONField(blank=True, null=True)
    idNumber = models.JSONField(blank=True, null=True)
    taxNumber = models.JSONField(blank=True, null=True)
    vatCode = models.JSONField(blank=True, null=True)
    jurisdiction = models.JSONField(blank=True, null=True)
    mainCountry = models.JSONField(blank=True, null=True)
    opencorporatesUrl = models.JSONField(blank=True, null=True)
    icijId = models.JSONField(blank=True, null=True)
    okpoCode = models.JSONField(blank=True, null=True)
    innCode = models.JSONField(blank=True, null=True)
    ogrnCode = models.JSONField(blank=True, null=True)
    leiCode = models.JSONField(blank=True, null=True)
    dunsCode = models.JSONField(blank=True, null=True)
    uniqueEntityId = models.JSONField(blank=True, null=True)
    npiCode = models.JSONField(blank=True, null=True)
    swiftBic = models.JSONField(blank=True, null=True)
    parent = models.JSONField(blank=True, null=True)

    cageCode = models.JSONField(blank=True, null=True)
    permId = models.JSONField(blank=True, null=True)
    imoNumber = models.JSONField(blank=True, null=True)
    giiNumber = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Public Body {self.name}"

    class Meta:
        verbose_name_plural = "Public Bodies"


class Employment(models.Model):
    sanctionEntity = models.OneToOneField(
        SanctionedEntity,
        on_delete=models.CASCADE,
    )

    details = models.JSONField(blank=True, null=True)
    role = models.JSONField(blank=True, null=True)
    status = models.JSONField(blank=True, null=True)
    employer = models.JSONField(blank=True, null=True)
    employee = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Employment of {self.employee} at {self.employer}"

    class Meta:
        verbose_name_plural = "Employments"


class Payment(models.Model):
    sanctionEntity = models.OneToOneField(
        SanctionedEntity,
        on_delete=models.CASCADE,
    )
    payer = models.JSONField(blank=True, null=True)
    beneficiary = models.JSONField(blank=True, null=True)
    startDate = models.JSONField(blank=True, null=True)
    endDate = models.JSONField(blank=True, null=True)
    date = models.JSONField(blank=True, null=True)
    summary = models.JSONField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    recordId = models.JSONField(blank=True, null=True)
    sourceUrl = models.JSONField(blank=True, null=True)
    publisher = models.JSONField(blank=True, null=True)
    modifiedAt = models.JSONField(blank=True, null=True)
    amount = models.JSONField(blank=True, null=True)
    currency = models.JSONField(blank=True, null=True)
    amountUsd = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Payments"

    def __str__(self):
        return (
            self.summary.get("value", "Unnamed Payment")
            if self.summary
            else "Unnamed Payment"
        )


class Address(models.Model):
    sanctionEntity = models.OneToOneField(
        SanctionedEntity,
        on_delete=models.CASCADE,
    )
    name = models.JSONField(blank=True, null=True)
    summary = models.JSONField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    country = models.JSONField(blank=True, null=True)
    alias = models.JSONField(blank=True, null=True)
    previousName = models.JSONField(blank=True, null=True)
    weakAlias = models.JSONField(blank=True, null=True)
    sourceUrl = models.JSONField(blank=True, null=True)
    publisher = models.JSONField(blank=True, null=True)
    wikidataId = models.JSONField(blank=True, null=True)
    keywords = models.JSONField(blank=True, null=True)
    topics = models.JSONField(blank=True, null=True)
    address = models.JSONField(blank=True, null=True)
    addressEntity = models.JSONField(blank=True, null=True)
    program = models.JSONField(blank=True, null=True)
    notes = models.JSONField(blank=True, null=True)
    createdAt = models.JSONField(blank=True, null=True)
    modifiedAt = models.JSONField(blank=True, null=True)
    full = models.JSONField(blank=True, null=True)
    remarks = models.JSONField(blank=True, null=True)
    postOfficeBox = models.JSONField(blank=True, null=True)
    street = models.JSONField(blank=True, null=True)
    city = models.JSONField(blank=True, null=True)
    postalCode = models.JSONField(blank=True, null=True)
    region = models.JSONField(blank=True, null=True)
    state = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Addresses"

    def __str__(self):
        return (
            self.name.get("value", "Unnamed Address")
            if self.name
            else "Unnamed Address"
        )


class Debt(models.Model):
    sanctionEntity = models.OneToOneField(
        SanctionedEntity,
        on_delete=models.CASCADE,
    )
    debtor = models.JSONField(blank=True, null=True)
    creditor = models.JSONField(blank=True, null=True)
    startDate = models.JSONField(blank=True, null=True)
    endDate = models.JSONField(blank=True, null=True)
    date = models.JSONField(blank=True, null=True)
    summary = models.JSONField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    recordId = models.JSONField(blank=True, null=True)
    sourceUrl = models.JSONField(blank=True, null=True)
    publisher = models.JSONField(blank=True, null=True)
    modifiedAt = models.JSONField(blank=True, null=True)
    amount = models.JSONField(blank=True, null=True)
    currency = models.JSONField(blank=True, null=True)
    amountUsd = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Debts"

    def __str__(self):
        return (
            self.summary.get("value", "Unnamed Debt")
            if self.summary
            else "Unnamed Debt"
        )


class UnknownLink(models.Model):
    sanctionEntity = models.OneToOneField(
        SanctionedEntity,
        on_delete=models.CASCADE,
    )
    subject = models.JSONField(blank=True, null=True)
    object = models.JSONField(blank=True, null=True)
    startDate = models.JSONField(blank=True, null=True)
    endDate = models.JSONField(blank=True, null=True)
    date = models.JSONField(blank=True, null=True)
    summary = models.JSONField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    recordId = models.JSONField(blank=True, null=True)
    sourceUrl = models.JSONField(blank=True, null=True)
    publisher = models.JSONField(blank=True, null=True)
    modifiedAt = models.JSONField(blank=True, null=True)
    role = models.JSONField(blank=True, null=True)
    status = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Unknown Links"

    def __str__(self):
        return (
            self.summary.get("value", "Unnamed Link")
            if self.summary
            else "Unnamed Link"
        )


class Passport(models.Model):
    sanctionEntity = models.OneToOneField(
        SanctionedEntity,
        on_delete=models.CASCADE,
    )
    holder = models.JSONField(blank=True, null=True)
    type = models.JSONField(blank=True, null=True)
    country = models.JSONField(blank=True, null=True)
    number = models.JSONField(blank=True, null=True)
    authority = models.JSONField(blank=True, null=True)
    startDate = models.JSONField(blank=True, null=True)
    endDate = models.JSONField(blank=True, null=True)
    date = models.JSONField(blank=True, null=True)
    summary = models.JSONField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    recordId = models.JSONField(blank=True, null=True)
    sourceUrl = models.JSONField(blank=True, null=True)
    publisher = models.JSONField(blank=True, null=True)
    modifiedAt = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Passports"

    def __str__(self):
        return (
            self.number.get("value", "Unnamed Passport")
            if self.number
            else "Unnamed Passport"
        )


class Representation(models.Model):
    sanctionEntity = models.OneToOneField(
        SanctionedEntity,
        on_delete=models.CASCADE,
    )
    agent = models.JSONField(blank=True, null=True)
    client = models.JSONField(blank=True, null=True)
    startDate = models.JSONField(blank=True, null=True)
    endDate = models.JSONField(blank=True, null=True)
    date = models.JSONField(blank=True, null=True)
    summary = models.JSONField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    recordId = models.JSONField(blank=True, null=True)
    sourceUrl = models.JSONField(blank=True, null=True)
    publisher = models.JSONField(blank=True, null=True)
    modifiedAt = models.JSONField(blank=True, null=True)
    role = models.JSONField(blank=True, null=True)
    status = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Representations"

    def __str__(self):
        return (
            self.summary.get("value", "Unnamed Representation")
            if self.summary
            else "Unnamed Representation"
        )


class Occupancy(models.Model):
    sanctionEntity = models.OneToOneField(
        SanctionedEntity,
        on_delete=models.CASCADE,
    )
    startDate = models.JSONField(blank=True, null=True)
    endDate = models.JSONField(blank=True, null=True)
    date = models.JSONField(blank=True, null=True)
    summary = models.JSONField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    recordId = models.JSONField(blank=True, null=True)
    sourceUrl = models.JSONField(blank=True, null=True)
    publisher = models.JSONField(blank=True, null=True)
    modifiedAt = models.JSONField(blank=True, null=True)
    holder = models.JSONField(blank=True, null=True)
    post = models.JSONField(blank=True, null=True)
    status = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Occupancies"

    def __str__(self):
        return (
            self.summary.get("value", "Unnamed Occupancy")
            if self.summary
            else "Unnamed Occupancy"
        )


class Membership(models.Model):
    sanctionEntity = models.OneToOneField(
        SanctionedEntity,
        on_delete=models.CASCADE,
    )
    startDate = models.JSONField(blank=True, null=True)
    endDate = models.JSONField(blank=True, null=True)
    date = models.JSONField(blank=True, null=True)
    summary = models.JSONField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    recordId = models.JSONField(blank=True, null=True)
    sourceUrl = models.JSONField(blank=True, null=True)
    publisher = models.JSONField(blank=True, null=True)
    modifiedAt = models.JSONField(blank=True, null=True)
    role = models.JSONField(blank=True, null=True)
    status = models.JSONField(blank=True, null=True)
    member = models.JSONField(blank=True, null=True)
    organization = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Memberships"

    def __str__(self):
        return (
            self.role.get("value", "Unnamed Membership")
            if self.role
            else "Unnamed Membership"
        )


class Directorship(models.Model):
    sanctionEntity = models.OneToOneField(
        SanctionedEntity,
        on_delete=models.CASCADE,
    )
    startDate = models.JSONField(blank=True, null=True)
    endDate = models.JSONField(blank=True, null=True)
    date = models.JSONField(blank=True, null=True)
    summary = models.JSONField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    recordId = models.JSONField(blank=True, null=True)
    sourceUrl = models.JSONField(blank=True, null=True)
    publisher = models.JSONField(blank=True, null=True)
    modifiedAt = models.JSONField(blank=True, null=True)
    role = models.JSONField(blank=True, null=True)
    status = models.JSONField(blank=True, null=True)
    director = models.JSONField(blank=True, null=True)
    organization = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Directorships"

    def __str__(self):
        return (
            self.role.get("value", "Unnamed Directorship")
            if self.role
            else "Unnamed Directorship"
        )


class LegalEntity(models.Model):
    sanctionEntity = models.OneToOneField(
        SanctionedEntity,
        on_delete=models.CASCADE,
    )
    name = models.JSONField(blank=True, null=True)
    summary = models.JSONField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    country = models.JSONField(blank=True, null=True)
    alias = models.JSONField(blank=True, null=True)
    previousName = models.JSONField(blank=True, null=True)
    weakAlias = models.JSONField(blank=True, null=True)
    sourceUrl = models.JSONField(blank=True, null=True)
    publisher = models.JSONField(blank=True, null=True)
    wikidataId = models.JSONField(blank=True, null=True)
    keywords = models.JSONField(blank=True, null=True)
    topics = models.JSONField(blank=True, null=True)
    address = models.JSONField(blank=True, null=True)
    addressEntity = models.JSONField(blank=True, null=True)
    program = models.JSONField(blank=True, null=True)
    notes = models.JSONField(blank=True, null=True)
    createdAt = models.JSONField(blank=True, null=True)
    modifiedAt = models.JSONField(blank=True, null=True)
    email = models.JSONField(blank=True, null=True)
    phone = models.JSONField(blank=True, null=True)
    website = models.JSONField(blank=True, null=True)
    legalForm = models.JSONField(blank=True, null=True)
    incorporationDate = models.JSONField(blank=True, null=True)
    dissolutionDate = models.JSONField(blank=True, null=True)
    status = models.JSONField(blank=True, null=True)
    sector = models.JSONField(blank=True, null=True)
    classification = models.JSONField(blank=True, null=True)
    registrationNumber = models.JSONField(blank=True, null=True)
    idNumber = models.JSONField(blank=True, null=True)
    taxNumber = models.JSONField(blank=True, null=True)
    vatCode = models.JSONField(blank=True, null=True)
    jurisdiction = models.JSONField(blank=True, null=True)
    mainCountry = models.JSONField(blank=True, null=True)
    opencorporatesUrl = models.JSONField(blank=True, null=True)
    icijId = models.JSONField(blank=True, null=True)
    okpoCode = models.JSONField(blank=True, null=True)
    innCode = models.JSONField(blank=True, null=True)
    ogrnCode = models.JSONField(blank=True, null=True)
    leiCode = models.JSONField(blank=True, null=True)
    dunsCode = models.JSONField(blank=True, null=True)
    uniqueEntityId = models.JSONField(blank=True, null=True)
    npiCode = models.JSONField(blank=True, null=True)
    swiftBic = models.JSONField(blank=True, null=True)
    parent = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Legal Entities"

    def __str__(self):
        return (
            self.name.get("value", "Unnamed Legal Entity")
            if self.name
            else "Unnamed Legal Entity"
        )


class Security(models.Model):
    sanctionEntity = models.OneToOneField(
        SanctionedEntity,
        on_delete=models.CASCADE,
    )
    name = models.JSONField(blank=True, null=True)
    summary = models.JSONField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    country = models.JSONField(blank=True, null=True)
    alias = models.JSONField(blank=True, null=True)
    previousName = models.JSONField(blank=True, null=True)
    weakAlias = models.JSONField(blank=True, null=True)
    sourceUrl = models.JSONField(blank=True, null=True)
    publisher = models.JSONField(blank=True, null=True)
    wikidataId = models.JSONField(blank=True, null=True)
    keywords = models.JSONField(blank=True, null=True)
    topics = models.JSONField(blank=True, null=True)
    address = models.JSONField(blank=True, null=True)
    addressEntity = models.JSONField(blank=True, null=True)
    program = models.JSONField(blank=True, null=True)
    notes = models.JSONField(blank=True, null=True)
    createdAt = models.JSONField(blank=True, null=True)
    modifiedAt = models.JSONField(blank=True, null=True)
    amount = models.JSONField(blank=True, null=True)
    currency = models.JSONField(blank=True, null=True)
    amountUsd = models.JSONField(blank=True, null=True)
    isin = models.JSONField(blank=True, null=True)
    registrationNumber = models.JSONField(blank=True, null=True)
    ticker = models.JSONField(blank=True, null=True)
    figiCode = models.JSONField(blank=True, null=True)
    issuer = models.JSONField(blank=True, null=True)
    issueDate = models.JSONField(blank=True, null=True)
    maturityDate = models.JSONField(blank=True, null=True)
    type = models.JSONField(blank=True, null=True)
    classification = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name.get("value", "") if self.name else "Unnamed Security"

    class Meta:
        verbose_name_plural = "Securities"


class Interval(models.Model):
    sanctionEntity = models.OneToOneField(
        SanctionedEntity,
        on_delete=models.CASCADE,
    )
    startDate = models.JSONField(blank=True, null=True)
    endDate = models.JSONField(blank=True, null=True)
    date = models.JSONField(blank=True, null=True)
    summary = models.JSONField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    recordId = models.JSONField(blank=True, null=True)
    sourceUrl = models.JSONField(blank=True, null=True)
    publisher = models.JSONField(blank=True, null=True)
    modifiedAt = models.JSONField(blank=True, null=True)

    def __str__(self):
        return str(self.sanctionedEntity)

    class Meta:
        verbose_name_plural = "Intervals"


class Thing(models.Model):
    sanctionEntity = models.OneToOneField(
        SanctionedEntity,
        on_delete=models.CASCADE,
    )
    name = models.JSONField(blank=True, null=True)
    summary = models.JSONField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    country = models.JSONField(blank=True, null=True)
    alias = models.JSONField(blank=True, null=True)
    previousName = models.JSONField(blank=True, null=True)
    weakAlias = models.JSONField(blank=True, null=True)
    sourceUrl = models.JSONField(blank=True, null=True)
    publisher = models.JSONField(blank=True, null=True)
    wikidataId = models.JSONField(blank=True, null=True)
    keywords = models.JSONField(blank=True, null=True)
    topics = models.JSONField(blank=True, null=True)
    address = models.JSONField(blank=True, null=True)
    addressEntity = models.JSONField(blank=True, null=True)
    program = models.JSONField(blank=True, null=True)
    notes = models.JSONField(blank=True, null=True)
    createdAt = models.JSONField(blank=True, null=True)
    modifiedAt = models.JSONField(blank=True, null=True)

    def __str__(self):
        return str(self.sanctionedEntity)

    class Meta:
        verbose_name_plural = "Things"


class Value(models.Model):
    sanctionEntity = models.OneToOneField(
        SanctionedEntity,
        on_delete=models.CASCADE,
    )
    amount = models.JSONField(blank=True, null=True)
    currency = models.JSONField(blank=True, null=True)
    amountUsd = models.JSONField(blank=True, null=True)

    def __str__(self):
        return str(self.sanctionedEntity)

    class Meta:
        verbose_name_plural = "Values"


class Interest(models.Model):
    sanctionEntity = models.OneToOneField(
        SanctionedEntity,
        on_delete=models.CASCADE,
    )
    startDate = models.JSONField(blank=True, null=True)
    endDate = models.JSONField(blank=True, null=True)
    date = models.JSONField(blank=True, null=True)
    summary = models.JSONField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    recordId = models.JSONField(blank=True, null=True)
    sourceUrl = models.JSONField(blank=True, null=True)
    publisher = models.JSONField(blank=True, null=True)
    modifiedAt = models.JSONField(blank=True, null=True)
    role = models.JSONField(blank=True, null=True)
    status = models.JSONField(blank=True, null=True)

    def __str__(self):
        return str(self.sanctionedEntity)

    class Meta:
        verbose_name_plural = "Interests"


class Vehicle(models.Model):
    sanctionEntity = models.OneToOneField(
        SanctionedEntity,
        on_delete=models.CASCADE,
    )
    name = models.JSONField(blank=True, null=True)
    summary = models.JSONField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    country = models.JSONField(blank=True, null=True)
    alias = models.JSONField(blank=True, null=True)
    previousName = models.JSONField(blank=True, null=True)
    weakAlias = models.JSONField(blank=True, null=True)
    sourceUrl = models.JSONField(blank=True, null=True)
    publisher = models.JSONField(blank=True, null=True)
    wikidataId = models.JSONField(blank=True, null=True)
    keywords = models.JSONField(blank=True, null=True)
    topics = models.JSONField(blank=True, null=True)
    address = models.JSONField(blank=True, null=True)
    addressEntity = models.JSONField(blank=True, null=True)
    program = models.JSONField(blank=True, null=True)
    notes = models.JSONField(blank=True, null=True)
    createdAt = models.JSONField(blank=True, null=True)
    modifiedAt = models.JSONField(blank=True, null=True)
    amount = models.JSONField(blank=True, null=True)
    currency = models.JSONField(blank=True, null=True)
    amountUsd = models.JSONField(blank=True, null=True)
    registrationNumber = models.JSONField(blank=True, null=True)
    type = models.JSONField(blank=True, null=True)
    model = models.JSONField(blank=True, null=True)
    owner = models.JSONField(blank=True, null=True)
    buildDate = models.JSONField(blank=True, null=True)

    def __str__(self):
        return str(self.sanctionedEntity)

    class Meta:
        verbose_name_plural = "Vehicles"
