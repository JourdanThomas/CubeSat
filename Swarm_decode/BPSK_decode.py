from gnuradio import analog, blocks, digital, gr
import threading

class BPSKReceiver(gr.top_block):
    def __init__(self, freq, samp_rate=48000):
        super().__init__()

        # Replace analog.sig_source with actual SDR source in real use
        self.src = analog.sig_source_c(samp_rate, analog.GR_SIN_WAVE, freq, 1, 0)
        
        # BPSK demodulator
        self.demod = digital.psk.psk_demod(
            constellation_points=2,
            differential=True,
            samples_per_symbol=2,
            excess_bw=0.35,
            phase_bw=0.0628,
            timing_bw=2*3.14/100.0,
            mod_code="none",
            verbose=False,
            log=False
        )

        self.sink = blocks.vector_sink_b()

        # Connect blocks
        self.connect(self.src, self.demod, self.sink)

def run_receiver(freq):
    rx = BPSKReceiver(freq)
    rx.start()
    rx.wait()
    print(f"Decoded stream at {freq}Hz:", rx.sink.data())

# Run 4 receivers in parallel
frequencies = [1000, 2000, 3000, 4000]
threads = [threading.Thread(target=run_receiver, args=(f,)) for f in frequencies]

for t in threads:
    t.start()
for t in threads:
    t.join()
