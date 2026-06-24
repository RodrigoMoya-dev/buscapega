import { redirect } from "next/navigation";

// "Validar sitio" se fusionó dentro de la vista Portales (/authenticate).
// Esta ruta queda como redirección para enlaces antiguos.
export default function ValidateRedirect() {
  redirect("/authenticate");
}
