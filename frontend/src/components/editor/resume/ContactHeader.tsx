import type { ContactInfo } from "@/lib/types";
import { Mail, Phone, MapPin, Link } from "lucide-react";

export function ContactHeader({ contact }: { contact: ContactInfo }) {
  return (
    <div className="border-b border-neutral-200 pb-5">
      <h1 className="text-2xl font-bold tracking-tight text-neutral-900">{contact.name}</h1>
      <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1">
        {contact.email && (
          <span className="flex items-center gap-1 text-xs text-neutral-500">
            <Mail className="h-3 w-3" /> {contact.email}
          </span>
        )}
        {contact.phone && (
          <span className="flex items-center gap-1 text-xs text-neutral-500">
            <Phone className="h-3 w-3" /> {contact.phone}
          </span>
        )}
        {contact.location && (
          <span className="flex items-center gap-1 text-xs text-neutral-500">
            <MapPin className="h-3 w-3" /> {contact.location}
          </span>
        )}
        {contact.linkedin && (
          <span className="flex items-center gap-1 text-xs text-neutral-500">
            <Link className="h-3 w-3" /> {contact.linkedin}
          </span>
        )}
        {contact.github && (
          <span className="flex items-center gap-1 text-xs text-neutral-500">
            <Link className="h-3 w-3" /> {contact.github}
          </span>
        )}
      </div>
    </div>
  );
}
