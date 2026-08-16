import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Praxis MVP",
  description: "Système de travail intelligent personnel",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr">
      <body style={{ fontFamily: 'system-ui, sans-serif', margin: 0, padding: '20px' }}>
        {children}
      </body>
    </html>
  );
}
