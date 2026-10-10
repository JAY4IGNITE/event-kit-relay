import { Section } from "@/components/ui/Section";
import { Reveal } from "@/components/motion/Reveal";

export function Testimonial() {
  return (
    <Section tint>
      <Reveal className="mx-auto max-w-3xl">
        <blockquote className="text-2xl font-medium leading-snug tracking-[-0.01em] text-fg md:text-[1.75rem]">
          The relay used to live on a whiteboard and a group chat. A late return now reshuffles the
          day on its own, and nobody argues about who scratched the lens.
        </blockquote>
        <figcaption className="mt-7 flex items-center gap-3.5">
          <img
            src="https://picsum.photos/seed/relay-priya-raman-portrait/128/128"
            alt=""
            loading="lazy"
            width={48}
            height={48}
            className="h-12 w-12 rounded-full object-cover grayscale"
          />
          <div className="text-sm leading-tight">
            <div className="font-medium text-fg">Priya Raman</div>
            <div className="text-fg-muted">AV Resource Office, Northgate College</div>
          </div>
        </figcaption>
      </Reveal>
    </Section>
  );
}
