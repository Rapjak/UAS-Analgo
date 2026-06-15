class KonfigurasiKendaraan:

    def __init__(
        self,
        beban_awal: float,
        beban_per_stop: list,
        beban_maks: float,
        rasio_penuh: float = 0.05,
        rasio_kosong: float = 0.02,
    ):
        self.beban_awal = beban_awal
        self.beban_per_stop = beban_per_stop
        self.beban_maks = beban_maks
        self.rasio_penuh = rasio_penuh
        self.rasio_kosong = rasio_kosong


def hitung_bensin(
    rute: list,
    matriks: list,
    cfg: KonfigurasiKendaraan,
    hub: int = 0,
):

    beban_map = {
        i: w
        for i, w in enumerate(cfg.beban_per_stop)
    }

    beban_sekarang = cfg.beban_awal

    total_liter = 0.0
    detail_segmen = []

    for i in range(len(rute) - 1):

        asal = rute[i]
        tujuan = rute[i + 1]

        jarak = matriks[asal][tujuan]

        rasio = (
            cfg.rasio_kosong
            + (beban_sekarang / cfg.beban_maks)
            * (cfg.rasio_penuh - cfg.rasio_kosong)
        )

        liter_segmen = jarak * rasio

        detail_segmen.append({
            "dari": asal,
            "ke": tujuan,
            "jarak_km": jarak,
            "beban_kg": round(beban_sekarang, 3),
            "rasio_L_km": round(rasio, 6),
            "liter": round(liter_segmen, 4),
        })

        total_liter += liter_segmen

        if tujuan != hub:
            beban_sekarang = max(
                0.0,
                beban_sekarang - beban_map.get(tujuan, 0.0)
            )

    return round(total_liter, 4), detail_segmen