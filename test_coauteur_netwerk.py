from coauteur_netwerk import (
    bouw_coauteur_netwerk,
    vind_publicatieconnectie
)


netwerk = bouw_coauteur_netwerk()


print()
print("=" * 70)
print("TEST CO-AUTEURNETWERK")
print("=" * 70)


for persoon_id, naam in netwerk["namen"].items():
    print(
        persoon_id,
        "->",
        naam
    )


print()
print("=" * 70)
print("ALLE SPIDER-CONNECTIES")
print("=" * 70)


persoon_ids = list(
    netwerk["namen"].keys()
)


for index, persoon_id_1 in enumerate(
    persoon_ids
):

    for persoon_id_2 in persoon_ids[
        index + 1:
    ]:

        resultaat = vind_publicatieconnectie(
            persoon_id_1,
            persoon_id_2,
            netwerk
        )

        if resultaat["type"] == "geen":
            continue


        naam_1 = netwerk[
            "namen"
        ][persoon_id_1]

        naam_2 = netwerk[
            "namen"
        ][persoon_id_2]


        print()
        print(
            naam_1,
            "<->",
            naam_2
        )

        print(
            resultaat
        )